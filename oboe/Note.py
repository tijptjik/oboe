import os
import sys
import regex as re
from oboe.utils import slug_case, md_link, render_markdown, find_tags
from oboe.format import (
    format_tags, format_blockrefs, format_highlights, format_links, format_code_blocks
)
from oboe.Link import Link
from oboe import LOG
from oboe import GLOBAL
import copy


class Note:
    def __init__(self, path):
        self.path = path
        self.filename = os.path.split(path)[-1]
        self.title = self.filename.replace(".md", "")
        self.filename_html = slug_case(self.title) + ".html"
        self.out_path = os.path.join(GLOBAL.OUTPUT_DIR, os.path.relpath(path, GLOBAL.VAULT_ROOT))
        self.out_path = os.path.join(os.path.split(self.out_path)[0], self.filename_html)

        self.link = Link(self.title)

        with open(path, encoding="utf8") as f:
            self.content = f.read()

        self.backlink_html = ""

        self.links = self.links_in_file()
        self.tags = find_tags(self.content)

        self.convert_obsidian_syntax()

    def links_in_file(self):
        """Returns a list of all links in the note."""
        matches = re.finditer(r"(!)?\[{2}(.*?)\]{2}", self.content)

        links = []
        for match in matches:
            link = Link(match.group(2), embed=match.group(1))
            links.append(link)

        return links

    def find_backlinks(self, others):
        """Returns a list of Link objects linking to all the notes in 'others' that reference self"""
        backlinks = []
        for other in others:
            if self == other: continue
            if self.link in other.links:
                backlinks.append(other.link)

        backlinks = sorted(backlinks, key=lambda link: link.path)

        return backlinks

    def convert_obsidian_syntax(self):
        """Converts Obsidian syntax into Markdown."""
        self.content = format_code_blocks(self.content)
        self.content = format_links(self.content, self.links)
        self.content = format_tags(self.content, self.tags)
        self.content = format_blockrefs(self.content)
        self.content = format_highlights(self.content)


    def html(self, oboe=False):
        """Returns the note formatted as HTML. Will use markdown2 as default, with the option of my own processor (WIP)"""
        # LOG.debug(f"Converting {self.title} into HTML...")

        if oboe:
            from oboe.markdown import convert
            html = convert(self.content)
        else:
            html = render_markdown(self.content)

        # Wrapping converted markdown in a div for styling
        html = f"<div id=\"content\">{html}</div>"



        # LOG.debug(f"{self.title} converted into HTML and placed inside div with id=\"content\"")

        return html

    def __eq__(self, other):
        return self.path == other.path

