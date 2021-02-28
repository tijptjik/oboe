import regex as re
from oboe.utils import slug_case, md_link
from oboe import LOG

LINK_SYNTAX = {
    "#": "header",
    "|": "alias",
    "#^": "blockref"
}

class Link:
    def __init__(self, obsidian_link, embed=None):
        self.obsidian_link = obsidian_link
        extended_link = re.match(r"([^#|^\n]+)([#|]\^?)(.*)", obsidian_link)
        
        if extended_link:
            self.file = extended_link.group(1)
            print("EXT_LINK: " + str(self.file))
            setattr(self, LINK_SYNTAX[extended_link.group(2)], extended_link.group(3))
        else:
            # Need to get the relative path to this file
            self.file = obsidian_link
            
        if embed:
            # Is embed, run function to get the content of the link destination
            self.content = self.get_content()
        
        self.slug = slug_case(self.file)
        #print(vault.notes[0])
        
    def get_content(self):
        """Gets the content residing at the link destination"""
        pass
        
    def md_link(self):
        """Returns a link string that follows the Markdown specification"""
        if hasattr(self, "alias"):
            alias = getattr(self, "alias")
            return md_link(alias, self.slug)
        elif hasattr(self, "header"):
            header = getattr(self, "header")
            return md_link(header, f"{self.slug}#{slug_case(header)}")
        elif hasattr(self, "blockref"):
            blockref = getattr(self, "blockref")
            return md_link(self.file, f"{self.slug}#{blockref}")
        else:
            return md_link(self.file, self.slug)
        
    def __eq__(self, other):
        return self.file == other.file