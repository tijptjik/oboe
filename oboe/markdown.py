import regex as re
from hashlib import sha256
from random import randint
from oboe.utils import slug_case


SALT = bytes(randint(0, 1000000))
def hash_text(text):
    return "md5-" + sha256(SALT + text.encode("utf-8")).hexdigest()[32:]
escape_table = dict([(ch, hash_text(ch)) for ch in '\\`*_{}[]()>#+-.!'])

# Precompiled regexes
whitespace_only_re = re.compile(r"^[ \t]+$", re.M)
fenced_code_block_re = re.compile(r"```(.*)$\n([\S\s]*?)\n```", re.M)
footnote_refs_re = re.compile(r"\[\^([\p{L}\p{N}_.-]+?)\](?!:)")
footnote_inline_re = re.compile(r"\^\[(.*?)\]")
link_def_re = re.compile(r"""^[ ]{0,3}\[(.+)\]:[ \t]*\n?[ \t]*<?(.+?)>?[ \t]*(?:\n?[ \t]*(?<=\s)['"(]([^\n]*)['")][ \t]*)?(?:\n+|\Z)""", re.M | re.U)
header_re = re.compile(r"(^(.+)[ \t]*\n(=+|-+)[ \t]*\n+)|(^(\#{1,6})[ \t]+(.+?)[ \t]*(?<!\\)\#*\n+)", re.M)
hr_re = re.compile(r"^[ ]{0,3}([-_*][ ]{0,2}){3,}$", re.M)
code_span_re = re.compile(r"(?<!\\)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)
html_token_re = re.compile(r"""(</?(?:\w+)(?:\s+(?:[\w-]+:)?[\w-]+=(?:".*?"|'.*?'))*\s*/?>|<\w+[^>]*>|<!--.*?-->|<\?.*?\?>)""")
inline_link_re = re.compile(r"""\[(.*?)\]\((.*?) ?(?:"(.*?)")?\)""")


def convert(text):
    """Convert the given text."""

    # Standardize line endings:
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Make sure text ends with a couple of newlines:
    text += "\n\n"

    # Convert all tabs to 4 spaces, as they should be
    if "\t" in text:
        detabbed = []
        for line in text.splitlines():
            if "\t" in line:
                detabbed.append(detab_line(line))
        text = "\n".join(detabbed)

    # Strip any lines consisting only of spaces and tabs, to simplify regexes.
    text = whitespace_only_re.sub("", text)
    
    # TODO: Metadata
    
    # Format fenced code blocks
    text = format_fenced_code_blocks(text)

    # Format footnotes
    text = format_footnotes(text)

    # Format link definitions (Not done yet)
    text = format_link_definitions(text)

    # Format all headers
    text = format_headers(text)
    
    # Format horisontal rules
    text = format_hr(text)
    
    # Format lists
    text = format_lists(text)

    # Format inline code
    text = format_inline_code(text)

    # Escape some Markdown characters that are present inside HTML tags, to avoid converting them
    text = escape_markdown_in_html(text)

    # Format inline links
    text = format_inline_links(text)

    # Format automatic links
    text = format_automatic_links(text)
    
    # text = self._encode_amps_and_angles(text)

    # if "strike" in self.extras:
    #     text = self._do_strike(text)

    # if "underline" in self.extras:
    #     text = self._do_underline(text)

    # text = self._do_italics_and_bold(text)

    # # Do hard breaks:
    # text = re.sub(r" *\n", "<br%s\n" % self.empty_element_suffix, text)

    # text = self._unescape_special_chars(text)

    text += "\n"

    # # Attach attrs to output
    # rv = UnicodeWithAttrs(text)

    return text
    

def detab_line(line):
    if "\t" not in line:
        return line
    chunk1, chunk2 = line.split("\t", 1)
    chunk1 += (" " * (4 - len(chunk1) % 4))
    return detab_line(chunk1 + chunk2)


def format_fenced_code_blocks(text):
    matches = fenced_code_block_re.finditer(text)
    for match in matches:
        # Format as plaintext if no language specified
        lang = match.group(1) if match.group(1) else "plaintext"
        text = text.replace(match.group(),
                    f"<pre><code class=\"{lang} lang-{lang} language-{lang}\">{match.group(2)}</code></pre>")
    return text


def format_footnotes(text):
    footnote_html_section = ""
    footnote_number = 1
    # First find regular footnotes
    footnote_refs = footnote_refs_re.finditer(text)
    for ref in footnote_refs:
        id = ref.group(1)
        if f"[^{id}]:" in text:
            footnote_def_re = re.compile(f"^ {{0,3}}\\[\\^{id}\\]: ?((?:\\s*.*\\n+)(?:^ {{4}}\\s*.*$\\n*)*)", re.MULTILINE)
            footnote = footnote_def_re.search(text)
            # Remove footnote definitions
            text = text.replace(footnote.group(), "")
            # Replace references with their HTML equivalent
            text = text.replace(ref.group(), f"<sup id=\"fn-{id}-ref\" class=\"footnote-ref\"><a href=\"#fn-{id}\" class=\"footnote-link\">[{footnote_number}]</a></sup>")
            # Add footnotes as li element
            footnote_html_section += f"<li id=\"fn-{id}\" class=\"footnote\">{footnote.group(1)}<a class=\"footnote-backref\" href=\"fn-{id}-ref\">↩︎</a></li>"
            footnote_number += 1
            
    # Then find inline footnotes
    footnote_refs = footnote_inline_re.finditer(text)
    for ref in footnote_refs:
        # Replace references with their HTML equivalent
        text = text.replace(ref.group(), f"<sup id=\"fn-{footnote_number}-ref\" class=\"footnote-ref\"><a href=\"#fn-{footnote_number}\" class=\"footnote-link\">[{footnote_number}]</a></sup>")
        # Add footnotes as li element
        footnote_html_section += f"<li id=\"fn-{footnote_number}\" class=\"footnote\">{ref.group(1)}<a class=\"footnote-backref\" href=\"fn-{footnote_number}-ref\">↩︎</a></li>"

    # Lastly add the footnote section at the end of the document
    if footnote_html_section:
        text += f"<section class=\"footnotes\"><hr>\n{footnote_html_section}\n</section>"
        
    return text


def format_link_definitions(text):
    # TODO: Not very important, will implement later. See regex `link_def_re`
    return text


def format_headers(text):
    matches = header_re.finditer(text)
    for match in matches:
        if match.group(1) is not None and match.group(3) == "-":
            return match.group(1)
        elif match.group(1) is not None:
            header_level = {"=": 1, "-": 2}[match.group(3)[0]]
            header_text = match.group(2)
        else:
            header_level = len(match.group(5))
            header_text = match.group(6)
            
        id = slug_case(header_text)
        header_html = format_span(header_text)
        text = text.replace(match.group(), f"<h{header_level} id=\"{id}\">{header_html}</h{header_level}>\n")
        
    return text


def format_hr(text):
    matches = hr_re.finditer(text)
    for match in matches:
        text = text.replace(match.group(), "\n<hr>\n")
    return text


def format_lists(text):
    pass


def format_inline_code(text):
    matches = code_span_re.finditer(text)
    for match in matches:
        code = match.group(2).strip(" \t")
        replacements = [("&", "&amp;"), ("<", "&lt;"), (">", "&gt;")]
        for before, after in replacements:
            code = code.replace(before, after)
        text = text.replace(match.group(), f"<code>{code}</code>")
    
    return text


def escape_markdown_in_html(text):
    escaped = []; in_html = False
    for part in html_token_re.split(text):
        if in_html:
            escaped.append(part.replace('*', escape_table['*']).replace('_', escape_table['_']))
        else:
            for char, escape in escape_table.items():
                part = part.replace("\\" + char, escape)
            escaped.append(part)
        in_html = not in_html
    return ''.join(escaped)


def format_inline_links(text):
    matches = inline_link_re.finditer(text)
    for match in matches:
        link_text = match.group(1)
        link_destination = match.group(2)
        link_title = match.group(3)
        attrs = " ".join([f"href=\"{link_destination}\"", f"title=\"{link_title}\"" if link_title else ""])
        text = text.replace(match.group(), f"<a {attrs}>{link_text}</a>")
        
    return text

def format_automatic_links(text):
    # TODO: Not a priority yet, but should get implemented soon
    return text