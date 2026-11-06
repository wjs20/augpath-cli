#!/usr/bin/env python3
import argparse
import os
import sys

import shtab
from boltons.pathutils import augpath


def stdin_records(separator):
    if separator == b"\n":
        for line in sys.stdin.buffer:
            yield line.removesuffix(separator)
        return

    pending = b""
    while chunk := sys.stdin.buffer.read1(65536):
        *records, pending = (pending + chunk).split(separator)
        yield from records
    if pending:
        yield pending


def main():
    parser = argparse.ArgumentParser(
        description="Augment paths supplied as arguments or read from stdin."
    )
    parser.add_argument("--suffix", default="", help="Insert before the extension")
    parser.add_argument("--prefix", default="", help="Insert before the basename")
    parser.add_argument("--ext", help="Replace the extension, including the dot")
    parser.add_argument("--base", help="Replace the basename without the extension")
    parser.add_argument("--dpath", help="Replace the directory")
    parser.add_argument("--multidot", action="store_true", help="Split at the first dot")
    parser.add_argument("-0", "--null", action="store_true", help="Use NUL record separators")
    parser.add_argument("-f", "--field", type=int, metavar="N", help="Augment field N, starting at 1")
    parser.add_argument("-d", "--delimiter", help="Literal field separator (default: tab)")
    parser.add_argument(
        "--append", action="store_true",
        help="Insert the augmented path after the selected field",
    )
    parser.add_argument("records", nargs="*", help="Read from stdin if omitted").complete = shtab.FILE
    shtab.add_argument_to(parser, "--print-completion")
    args = parser.parse_args()

    if not args.records and sys.stdin.isatty():
        parser.error("supply paths or records as arguments or pipe them in on stdin")
    if args.field is not None and args.field < 1:
        parser.error("--field must be at least 1")
    if args.delimiter is not None and args.field is None and not args.append:
        parser.error("--delimiter requires --field or --append")

    separator = b"\0" if args.null else b"\n"
    delimiter = os.fsencode("\t" if args.delimiter is None else args.delimiter)
    if not delimiter or separator in delimiter:
        parser.error("the field delimiter must be nonempty and cannot contain the record separator")

    records = map(os.fsencode, args.records) if args.records else stdin_records(separator)
    field_index = 0 if args.field is None else args.field - 1

    for record_number, record in enumerate(records, start=1):
        fields = [record] if args.field is None else record.split(delimiter)
        if field_index >= len(fields):
            parser.exit(1, f"{parser.prog}: record {record_number} has no field {args.field}\n")

        path = os.fsdecode(fields[field_index])
        result = augpath(
            path, suffix=args.suffix, prefix=args.prefix, ext=args.ext,
            base=args.base, dpath=args.dpath, multidot=args.multidot,
        )
        encoded_result = os.fsencode(result)
        if args.append:
            fields.insert(field_index + 1, encoded_result)
        else:
            fields[field_index] = encoded_result

        sys.stdout.buffer.write(delimiter.join(fields) + separator)


if __name__ == "__main__":
    main()
