"""Command modules for OARC Crawlers CLI."""

from oarc_crawlers.cli.cmd.arxiv_cmd import arxiv
from oarc_crawlers.cli.cmd.build_cmd import build
from oarc_crawlers.cli.cmd.config_cmd import config
from oarc_crawlers.cli.cmd.ddg_cmd import ddg
from oarc_crawlers.cli.cmd.gh_cmd import gh
from oarc_crawlers.cli.cmd.mcp_cmd import mcp
from oarc_crawlers.cli.cmd.publish_cmd import publish
from oarc_crawlers.cli.cmd.web_cmd import web
from oarc_crawlers.cli.cmd.yt_cmd import yt


__all__ = [
    "arxiv",
    "build",
    "config",
    "ddg",
    "gh",
    "mcp",
    "publish",
    "web",
    "yt"
]
