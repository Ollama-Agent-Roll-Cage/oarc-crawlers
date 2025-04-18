"""Main command-line interface for OARC Crawlers."""
import sys

from oarc_crawlers.cli import cli

def main(**kwargs):
    """Main CLI entry point."""
    return cli(standalone_mode=False, **kwargs)

if __name__ == "__main__":
    sys.exit(main())
