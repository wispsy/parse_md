# parse-md

Bounded, source-preserving Markdown parsing and safe typed HTML rendering.
Python 3.14+, with no runtime dependencies. Version 0.1.0 is an unpublished
candidate extracted from Pretty Notebook; see [provenance](PROVENANCE.md).

```python
from parse_md import EXTENDED, RendererContext, parse, render

document = parse('# Heading\n\n**Hello**.\n')
assert document.to_markdown() == '# Heading\n\n**Hello**.\n'
assert '<strong>Hello</strong>' in document.to_html()

result = render('| A | B |\n| --- | --- |\n| one | two |\n', dialect=EXTENDED)
assert '<table>' in result.html
```

The default CommonMark profile preserves original slices, code-point source
spans and bounded parsing. The opt-in extended profile adds generic document
tables, tasks, footnotes, attributes, TOC, strike/highlight, wiki/image syntax and
diagram metadata. Unknown syntax remains literal source. HTML is escaped by
default; `RendererContext(trust='trusted')` explicitly permits raw HTML and is
not sanitization.

Application callbacks resolve wiki/image destinations, filter tags, decorate
links or render explicitly selected node types. The engine imports no notebook
models, graph, routes, templates, icons, HTTP client or filesystem state. The
caller owns its application policy and any callback-produced HTML.

See [the API contract](docs/api.md) for immutable dialect identities, limits,
callbacks and extraction/adoption boundaries. Headless spreadsheet tables remain
separate values; any adapter is optional. Terminal layout belongs to Escape
Colors and HTML-tree processing to Astree.

Development and candidate qualification:

```sh
uv sync --locked
uv run --frozen python -m pytest
uv run --frozen python scripts/check_distribution.py --output-dir /tmp/parse-md-candidate
```

The implementation retains its MIT notices. The complete 652-example CommonMark
0.31.2 fixture corpus retains its separate CC BY-SA 4.0 attribution in
[tests/fixtures/markdown/NOTICE.md](tests/fixtures/markdown/NOTICE.md).
`release.yaml` uses the `pypi` environment and verifies tag/version/main before
publication; preparing or merging this candidate does not publish it.
