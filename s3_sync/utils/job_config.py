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
args = parser.parse_args()

is_dev_mode = args.dev

limit = f"LIMIT {str(args.limit)}" if args.limit > 0 else ""
