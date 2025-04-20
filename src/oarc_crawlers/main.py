"""OARC Crawlers Command-Line Interface."""
import sys

from oarc_crawlers.cli import cli
from oarc_decorators import handle_error


@handle_error
def main(**kwargs):
    """Run the CLI command."""
    return cli(standalone_mode=False, **kwargs)


if __name__ == "__main__":
    sys.exit(main())
