"""Placeholder script to seed test data in Odoo instances.
To be implemented once connectors are available.
"""

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("database")
    parser.add_argument("api_key")
    parser.add_argument("user", default="admin")
    parser.parse_args()
    # TODO: populate demo data via connectors
    print("setup-test-data not yet implemented")
    return 0


if __name__ == "__main__":
    sys.exit(main())
