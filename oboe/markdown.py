import regex as re
from oboe.utils import slug_case


# Precompiled regexes
whitespace_only_re = re.compile(r"^[ \t]+$", re.MULTILINE)
fenced_code_block_re = re.compile(r"```(.*)$\n([\S\s]*?)\n```", re.MULTILINE)
footnote_refs_re = re.compile(r"\[\^([\p{L}\p{N}_.-]+?)\](?!:)")
footnote_inline_re = re.compile(r"\^\[(.*?)\]")
link_def_re = re.compile(
    r"""^[ ]{0,3}\[(.+)\]:[ \t]*\n?[ \t]*<?(.+?)>?[ \t]*(?:\n?[ \t]*(?<=\s)['"(]([^\n]*)['")][ \t]*)?(?:\n+|\Z)""", re.M | re.U
)
header_re = re.compile(r"(^(.+)[ \t]*\n(=+|-+)[ \t]*\n+)|(^(\#{1,6})[ \t]+(.+?)[ \t]*(?<!\\)\#*\n+)", re.M)


def convert(self, text):
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

    # Strip any lines consisting only of spaces and tabs.
    # This makes subsequent regexen easier to write, because we can
    # match consecutive blank lines with /\n+/ instead of something
    # contorted like /[ \t]*\n+/ .
    text = whitespace_only_re.sub("", text)
    
    # Format fenced code blocks
    text = format_fenced_code_blocks(text)

    # Format footnotes
    text = format_footnotes(text)

    # Format link definitions (Not done yet)
    text = format_link_definitions(text)

    # Format all headers
    text = format_headers(text)

    # TODO: Continue here!
    text = self._run_block_gamut(text)

    if "footnotes" in self.extras:
        text = self._add_footnotes(text)

    text = self.postprocess(text)

    text = self._unescape_special_chars(text)

    if self.safe_mode:
        text = self._unhash_html_spans(text)
        # return the removed text warning to its markdown.py compatible form
        text = text.replace(self.html_removed_text, self.html_removed_text_compat)

    do_target_blank_links = "target-blank-links" in self.extras
    do_nofollow_links = "nofollow" in self.extras

    if do_target_blank_links and do_nofollow_links:
        text = self._a_nofollow_or_blank_links.sub(r'<\1 rel="nofollow noopener" target="_blank"\2', text)
    elif do_target_blank_links:
        text = self._a_nofollow_or_blank_links.sub(r'<\1 rel="noopener" target="_blank"\2', text)
    elif do_nofollow_links:
        text = self._a_nofollow_or_blank_links.sub(r'<\1 rel="nofollow"\2', text)

    if "toc" in self.extras and self._toc:
        self._toc_html = calculate_toc_html(self._toc)

        # Prepend toc html to output
        if self.cli:
            text = '{}\n{}'.format(self._toc_html, text)

    text += "\n"

    # Attach attrs to output
    rv = UnicodeWithAttrs(text)

    if "toc" in self.extras and self._toc:
        rv.toc_html = self._toc_html

    if "metadata" in self.extras:
        rv.metadata = self.metadata
    return rv
    

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
            n = len(match.group(5))
            header_text = match.group(6)
            
        id = slug_case(header_text)
        header_html = header_text
        text.replace(match.group(), f"<h{n} id=\"{id}\">{header_html}</h{n}>")