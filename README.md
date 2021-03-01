<div align="center"><sup><b>NOTE</b>: <code>obsidian-html</code> has been renamed to <code>oboe</code> in order to gradually decouple it from Obsidian. Apologies for the inconveniences this may cause. If you've already installed <code>obsidian-html</code>, you can uninstall it and follow the <a href="#installation">installation instructions</a> for <code>oboe</code> below. Be sure to also update your GitHub Actions.</sup></div>

<br>

<div align="center"><h1>Oboe</h1></div>

<p align="center">
  <a href="#installation">Installation</a> -
  <a href="#usage">Usage</a> -
  <a href="#tips">Tips</a>
</p>

Oboe is a Python command line tool made to convert an [Obsidian](https://obsidian.md/) vault into a vault of HTML files, with the goal of publishing them as static files. It depends on the excellent [markdown2](https://github.com/trentm/python-markdown2) by [trentm](https://github.com/trentm) for Markdown parsing, but also deals with parsing Obsidian's flavor of Markdown. In addition, Oboe handles the structure of your vault and supports templates.

# Installation

1. Make sure Python and PIP are installed.
2. Install Oboe with `pip install git+https://github.com/kmaasrud/oboe`

# Usage

Supply the path to an Obsidian vault, and Oboe will convert all its notes into HTML, appended by the notes' backlinks.

    oboe <path to vault>

These HTML-files are by default placed in the directory `./html`. To specify another output directory, use the flag `-o` or `--output-directory`.

    oboe <path to vault> -o <output directory>

## Sub-directories

By default, Oboe only converts notes in the vault root, and not those inside sub-directories. To include sub-directories, add them with the flag `-d` or `--sub-directories`. For example, say you have the folders `Daily notes` and `Zettels` that you want to have converted. In this case, run

    oboe <path to vault> -d "Daily notes" "Zettels"

## Templates

The output is not very exciting from the get-go. It needs some style and structure. This is done by using a HTML template. A template must have the formatters `{title}` and `{content}` present. Their value should be obvious. The template file is supplied to `obsidian-html` by the flag `-t` or `--template`, like this:

    oboe <path to vault> -t template.html

Here you can add metadata, link to CSS-files and add unified headers/footers to all the pages. [Here's](https://github.com/kmaasrud/brain/blob/master/template.html) an example of how I use the template function on my own hosted vault.

Note that because of the way Python does formatting, the template cannot contain single curly braces other than the abovementioned formatters. To include Javascript or CSS in your template, always use double curly braces (e.g. `{{`). These will be changed into single braces in the final result.

## Filtering notes by tag

Oboe supports only converting notes that contain a certain tag. The filter is specified via the `-f` or `--filter` flag. For example, say you had a tag `#physics` for notes relating to physics, and the same for `#chemistry`. To convert all notes relating to physics and/or chemistry, run Oboe like this:

    oboe <path to vault> -f physics chemistry

Filters are not strict, so Oboe will convert any notes containing any of the tags in the filter. Filters can also be negated by prefixing a tag with `.`, for example:

    oboe <path to vault> -f physics .chemistry

The above would convert all notes with the `#physics` tag, but exclude all notes with the `#chemistry` tag. If the filter contains only exclusions, Oboe will convert every note except those who match the exclusion.

## Other flags

- `-e` or `--add-file-extensions`: Most web-servers do not need the `.html` file extension in URLs to find the correct file. However, that might be needed when browsing the converted vault locally. If you experience issues with this or want all links to have a `.html` extension, just add this flag when running.

- `-b`or `--omit-backlink-dash`: Removes the `- ` in front of the backlink when inserted in html.

# Tips

## Publishing your vault automatically to GitHub Pages

Make a GitHub Actions workflow using the YAML below, and your vault will be published to GitHub Pages every time you push to the repository.

1. Make sure you have GitHub Pages set up in the vault, and that it has `gh-pages` `/root` as its source.
2. Copy and modify the following YAML job to match your repository. Add it to your vault repository as `.github/workflows/publish.yml`.

    ```yaml
    name: Publish to GitHub Pages

    on:
      push:
        branches: [ master ]

    jobs:
      deploy:
        runs-on: ubuntu-latest

        steps:
        - uses: actions/checkout@v2

        - name: Set up Python 3.8
          uses: actions/setup-python@v2
          with:
            python-version: 3.8

      - name: Install oboe
        run: |
          python -m pip install --upgrade pip
          pip install git+https://github.com/kmaasrud/oboe.git

      - name: Generate HTML through oboe
        run: oboe ./vault -o ./out -t ./template.html -d daily

      - name: Publish
        uses: s0/git-publish-subdir-action@develop
        env:
          REPO: self
          BRANCH: gh-pages
          FOLDER: out
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    ```
3. ????
4. PROFIT!!!

## Support for TeX via KaTeX

By loading KaTeX in the HTML template and initializing it with `$` and `$$` as delimiters, you will have TeX support on the exported documents.

Just add this to the bottom of you template's body:

```html
<!-- KaTeX -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.11.1/dist/katex.min.css"
  integrity="sha384-zB1R0rpPzHqg7Kpt0Aljp8JPLqbXI3bhnPWROx27a9N0Ll6ZP/+DiW/UqRcLbRjq" crossorigin="anonymous">

<!-- The loading of KaTeX is deferred to speed up page rendering -->
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.11.1/dist/katex.min.js"
  integrity="sha384-y23I5Q6l+B6vatafAwxRu/0oK/79VlbSz7Q9aiSZUvyWYIYsd+qj+o24G5ZU2zJz"
  crossorigin="anonymous"></script>

<!-- To automatically render math in text elements, include the auto-render extension: -->
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.11.1/dist/contrib/auto-render.min.js"
  integrity="sha384-kWPLUVMOks5AQFrykwIup5lo0m3iMkkHrD0uJ4H5cjeGihAutqP0yW0J6dpFiVkI"
  crossorigin="anonymous"></script>

<!-- Parsing single dollar signs -->
<script>
  document.addEventListener("DOMContentLoaded", function () {{
      renderMathInElement(document.body, {{
        delimiters: [
          {{left: "$$", right: "$$", display: true}},
        {{left: "\\[", right: "\\]", display: true}},
    {{left: "$", right: "$", display: false}},
    {{left: "\\(", right: "\\)", display: false}}
      ]
  }});
  }});
</script>
```

> Note the double `{`'s. This is to work around how Python formatting works, and will be correct in the outputted HTML.

## Syntax highlighting

Using [highlight.js](https://highlightjs.org/), syntax highlighting is easily achieved.

Just add this to the bottom of you template's body:

```html
<!-- Syntax highlighting through highlight.js -->
<link rel="stylesheet" href="https://unpkg.com/@highlightjs/cdn-assets@10.4.0/styles/default.min.css">
<script src="https://unpkg.com/@highlightjs/cdn-assets@10.4.0/highlight.min.js"></script>

<script>
  // Ignore highlighting of mermaid
  hljs.configure({{noHighlightRe: /^mermaid$/}});
  hljs.initHighlightingOnLoad();
</script>
```

> Note the double `{`'s. This is to work around how Python formatting works, and will be correct in the outputted HTML.
