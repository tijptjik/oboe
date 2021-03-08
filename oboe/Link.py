import regex as re
from oboe.utils import slug_case, md_link
from oboe import LOG
import os
from oboe import GLOBAL

LINK_SYNTAX = {
    "#": "header",
    "|": "alias",
    "#^": "blockref"
}

class Link:
    def __init__(self, text, embed=None):
        self.obsidian_link = text
        extended_link = re.match(r"([^#|^\n]+)([#|]\^?)(.*)", text)

        if extended_link:
            # Is extended link, set attribute corresponding to the correct link type
            self.path = os.path.join(*extended_link.group(1).split("/")) # Ensures correct path separators
            setattr(self, LINK_SYNTAX[extended_link.group(2)], extended_link.group(3))
            LOG.debug(f"Link(\"{text}\") is extended. self.path: {self.path}")
        else:
            # Is regular link, just set path
            self.path = os.path.join(*text.split("/")) # Ensures correct path separators
            LOG.debug(f"Link(\"{text}\") is not extended. self.path: {self.path}")

        if not os.path.isfile(os.path.join(GLOBAL.VAULT_ROOT, self.path + ".md")):
            LOG.debug("Link not absolute, trying relative...")

        if embed:
            # Is embed, run function to get the content of the link destination
            self.content = self.get_content()

        self.slug = "/".join(list(map(lambda x: slug_case(x), text.split("/"))))


    def get_content(self):
        """Gets the content residing at the link destination"""
        pass

    def md_link(self):
        # if self.slugpath:
        #     self.slug = self.slugpath
        """Returns a link string that follows the Markdown specification"""
        if hasattr(self, "alias"):
            alias = getattr(self, "alias")
            return md_link(alias, self.slug)
        elif hasattr(self, "header"):
            header = getattr(self, "header")
            return md_link(header, f"{self.slug}", extended=f"#{slug_case(header)}")
        elif hasattr(self, "blockref"):
            blockref = getattr(self, "blockref")
            return md_link(self.path, f"{self.slug}", extended=f"#{blockref}")
        else:
            return md_link(self.path, self.slug)

    def __eq__(self, other):
        return self.path == other.path
