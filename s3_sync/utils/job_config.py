import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--dev',
                    action='store_true',
                    help='Flag to indicate development environment',
                    )
parser.add_argument('--limit',
                    type=int,
                    default=0,
                    help='Limit number of rows to process',
                    )
parser.add_argument('--offset',
                    type=int,
                    default=0,
                    help='Offset number of rows to process',
                    )
args = parser.parse_args()

is_dev_mode = args.dev

offset = f"OFFSET {str(args.offset)}" if args.offset > 0 else ""

_limit = f"LIMIT {str(args.limit)}" if args.limit > 0 else ""

limit = f"{offset} {_limit}"
