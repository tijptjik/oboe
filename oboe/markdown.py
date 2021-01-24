 def convert(self, text):
        """Convert the given text."""
        # Main function. The order in which other subs are called here is
        # essential. Link and image substitutions need to happen before
        # _EscapeSpecialChars(), so that any *'s or _'s in the <a>
        # and <img> tags get encoded.

        # Clear the global hashes. If we don't clear these, you get conflicts
        # from other articles when generating a page which contains more than
        # one article (e.g. an index page that shows the N most recent
        # articles):
        self.reset()

        if not isinstance(text, unicode):
            # TODO: perhaps shouldn't presume UTF-8 for string input?
            text = unicode(text, 'utf-8')

        if self.use_file_vars:
            # Look for emacs-style file variable hints.
            emacs_vars = self._get_emacs_vars(text)
            if "markdown-extras" in emacs_vars:
                splitter = re.compile("[ ,]+")
                for e in splitter.split(emacs_vars["markdown-extras"]):
                    if '=' in e:
                        ename, earg = e.split('=', 1)
                        try:
                            earg = int(earg)
                        except ValueError:
                            pass
                    else:
                        ename, earg = e, None
                    self.extras[ename] = earg

        # Standardize line endings:
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Make sure $text ends with a couple of newlines:
        text += "\n\n"

        # Convert all tabs to spaces.
        text = self._detab(text)

        # Strip any lines consisting only of spaces and tabs.
        # This makes subsequent regexen easier to write, because we can
        # match consecutive blank lines with /\n+/ instead of something
        # contorted like /[ \t]*\n+/ .
        text = self._ws_only_line_re.sub("", text)

        # strip metadata from head and extract
        if "metadata" in self.extras:
            text = self._extract_metadata(text)

        text = self.preprocess(text)

        if "fenced-code-blocks" in self.extras and not self.safe_mode:
            text = self._do_fenced_code_blocks(text)

        if self.safe_mode:
            text = self._hash_html_spans(text)

        # Turn block-level HTML blocks into hash entries
        text = self._hash_html_blocks(text, raw=True)

        if "fenced-code-blocks" in self.extras and self.safe_mode:
            text = self._do_fenced_code_blocks(text)

        # Because numbering references aren't links (yet?) then we can do everything associated with counters
        # before we get started
        if "numbering" in self.extras:
            text = self._do_numbering(text)

        # Strip link definitions, store in hashes.
        if "footnotes" in self.extras:
            # Must do footnotes first because an unlucky footnote defn
            # looks like a link defn:
            #   [^4]: this "looks like a link defn"
            text = self._strip_footnote_definitions(text)
        text = self._strip_link_definitions(text)

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