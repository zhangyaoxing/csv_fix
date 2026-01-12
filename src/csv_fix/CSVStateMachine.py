#!/usr/bin/env python
import os
from logging import getLogger
from csv_fix.states import States


class CSVStateMachine:
    def __init__(self, config, output):
        self.seperator = config.separator
        self.qualifier = config.qualifier
        self.trim = config.trim
        # self.timezone = config.timezone
        self.skip_errors = config.skip_errors
        self.output = output
        self.state = States.QUALIFIER
        # input buffer for whole input line.
        self.buff = ""
        # position of character done recognizing
        self.base_pos = 0
        self.fields = []
        self.encoding = "utf8"
        self.logger = getLogger(__name__)

    def feed(self, buff):
        self.state = States.QUALIFIER
        self.fields = []
        self.base_pos = 0
        self.buff = buff
        length = len(buff)
        for _ in range(0, length):
            self._state_qualifier()
            self._state_qualifier_close()
            self._state_seperator()
            self._state_field()
            self._state_field_in_qualifier()
            if self.state == States.END or self.state == States.INVALID:
                break

        if self.state == States.END:
            self._state_end()
        else:
            self.logger.error("Couldn't parse this line: %s", self.buff)
            if not self.skip_errors:
                self.logger.error("-k set to stop on error. exiting...")
                exit(1)

    def _state_qualifier(self):
        if self.state == States.QUALIFIER:
            # TODO: BOM is not properly handled here. Fix it!
            psbl_qual = self.buff[self.base_pos : self.base_pos + len(self.qualifier)]
            if psbl_qual == self.qualifier and self.qualifier != "":
                # recognized qualifier
                self.base_pos += len(self.qualifier)
                self.state = States.FIELD_IN_QUALIFIER
            else:
                self.state = States.FIELD

    def _state_qualifier_close(self):
        if self.state == States.QUALIFIER_CLOSE:
            self.base_pos += len(self.qualifier)
            i = self.base_pos + 1
            string = self.buff[self.base_pos : i]
            if string in ["\r", "\n", ""]:
                self.state = States.END
            else:
                self.state = States.SEPARATOR

    def _state_seperator(self):
        if self.state == States.SEPARATOR:
            i = self.base_pos + len(self.seperator)
            psbl_sprt = self.buff[self.base_pos : i]
            if psbl_sprt == self.seperator:
                self.base_pos = i
                self.state = States.QUALIFIER
            # else:
            # Shouldn't happen since this is handled in "qualifier" state

    def _state_field(self):
        if self.state == States.FIELD:
            i = self.base_pos + 1
            psbl_end = self.buff[self.base_pos : i]
            if psbl_end in ["\r", "\n", ""]:
                # last field is empty
                self._push_field("")
                self.state = States.END
            else:
                i = self.base_pos
                while i < len(self.buff):
                    j = i + len(self.seperator)
                    psbl_end = self.buff[i:j]
                    if psbl_end == self.seperator:
                        field = self.buff[self.base_pos : i]
                        self._push_field(field)
                        self.state = States.SEPARATOR
                        self.base_pos = i
                        break
                    else:
                        j = i + 1
                        psbl_end = self.buff[j : j + 1]
                        if psbl_end in ["\r", "\n", ""]:
                            # end of line
                            field = self.buff[self.base_pos : j]
                            self._push_field(field)
                            self.state = States.END
                            break
                    j = i + len(self.qualifier)
                    curr_str = self.buff[i:j]
                    if curr_str == self.qualifier:
                        k = j + len(self.qualifier)
                        after = self.buff[j:k]
                        if after == self.qualifier:
                            i += len(self.qualifier)
                        else:
                            # escape current qualifier by repeat it once
                            self.buff = self.buff[:j] + self.qualifier + self.buff[j:]
                            i += len(self.qualifier)
                    i += 1

    def _state_field_in_qualifier(self):
        if self.state == States.FIELD_IN_QUALIFIER:
            i = self.base_pos
            while i < len(self.buff):
                j = i + len(self.qualifier)
                curr_str = self.buff[i:j]
                if curr_str == self.qualifier:
                    # closing qualifier detected
                    # if it's followed by seperator, then the field is closed
                    k = j + len(self.seperator)
                    followed_by = self.buff[j:k]
                    followed_one = self.buff[j : j + 1]
                    is_followed_by_end = (
                        followed_by == self.seperator
                        or followed_one in ["\r", "\n", ""]
                    )
                    # also try to detect qualifier escape. e.g. "".
                    # however field like "ab"" should not be treated as escape.
                    # depends on if 2nd qualifier is followed by a seperator or line end or EOF.
                    k = j + len(self.qualifier)
                    followed_by = self.buff[j:k]
                    l = k + len(self.seperator)
                    snd_followed_by = self.buff[k:l]
                    snd_followed_one = self.buff[k : k + 1]
                    is_followed_by_qual = followed_by == self.qualifier
                    is_qual_followed_by_end = (
                        snd_followed_by == self.seperator
                        or snd_followed_one in ["\r", "\n", ""]
                    )
                    if is_followed_by_end:
                        # qualifier is followed by seperator or line end or EOF.
                        field = self.buff[self.base_pos : i]
                        self._push_field(field)
                        self.state = States.QUALIFIER_CLOSE
                        self.base_pos = i
                        break
                    elif is_followed_by_qual and not is_qual_followed_by_end:
                        # This is escape, skip the immediate after qualifier and continue
                        i += len(self.qualifier)
                    else:
                        # escape current qualifier by repeat it once
                        self.buff = self.buff[:j] + self.qualifier + self.buff[j:]
                        i += len(self.qualifier)
                i += 1
            if self.state == States.FIELD_IN_QUALIFIER:
                # searched to the end still can't find closing qualifier. something is wrong.
                self.state = States.INVALID

    def _state_end(self):
        if self.state == States.END:
            self.base_pos = len(self.buff)
            line = ",".join([f'"{f}"' for f in self.fields]) + os.linesep
            self.output.write(line)
            self.output.flush()

    def _push_field(self, field):
        # TODO: handle time convertion
        if self.trim:
            field = field.strip()
        self.fields.append(field)

    def _detect_time(self):
        return
