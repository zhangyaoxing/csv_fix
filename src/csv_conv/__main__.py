#!/usr/bin/env python3
"""CSV Converter - A command line tool for CSV file processing."""

import argparse
import sys


def parse_args(args=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="csv_conv",
        description="CSV Converter - A tool for CSV file processing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-s",
        dest="separator",
        default=",",
        help="Define separator. Defaults to comma.",
    )

    parser.add_argument(
        "-q",
        dest="qualifier",
        default=None,
        help="Define text qualifier. Defaults to auto detect.",
    )

    parser.add_argument(
        "-t",
        dest="trim",
        action="store_true",
        default=False,
        help="Trim white space at the beginning and end of each field. Defaults to no trim.",
    )

    parser.add_argument(
        "-z",
        dest="timezone",
        default=None,
        help=(
            "Specify timezone for time fields. Defaults to server timezone. "
            "Can also be Asia/Chongqing etc. "
            "For standard timezone names, refer to: "
            "https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
        ),
    )

    parser.add_argument(
        "-k",
        dest="skip_errors",
        action="store_true",
        default=False,
        help="Skip errors and continue parsing following lines.",
    )

    parser.add_argument(
        "input_file",
        nargs="?",
        help="Input CSV file path. Read from stdin if not provided.",
    )

    return parser.parse_args(args)


def main():
    """Main entry point."""
    args = parse_args()

    # TODO: Implement CSV processing logic
    print(f"Separator: {args.separator!r}")
    print(f"Qualifier: {args.qualifier!r}")
    print(f"Trim: {args.trim}")
    print(f"Timezone: {args.timezone}")
    print(f"Skip errors: {args.skip_errors}")
    print(f"Input file: {args.input_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
