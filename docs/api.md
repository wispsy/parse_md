# Parser and rendering contract

`parse(source, dialect=COMMONMARK, options=ParseOptions())` returns immutable
document nodes with exact original source and half-open code-point spans.
`parse_blocks` exposes the block stage. `Node.to_markdown()` selects original
source when present; constructed nodes serialize deterministically. This is
not a promise to round-trip arbitrary constructed edits losslessly.

`COMMONMARK` identifies `commonmark-0.31.2-v1`; `EXTENDED` identifies
`extended-0.31.2-v1`. Built-in profiles share the existing parser character,
node, nesting and inline-work accounting. `Dialect` is immutable and only known
name/version pairs are accepted. The extended profile includes reusable table,
task, footnote, attribute, TOC, wiki/image and diagram syntax. The profile owns
syntax; applications own its meaning. Arbitrary block/inline parser callbacks
are deliberately outside 0.1 until their shared-budget contract is selected.

Defaults are 2,000,000 source characters, 100,000 nodes and 64 nesting levels.
Lower caller limits are supported; nesting cannot exceed 64. Inline work is
bounded to 32 steps per character with a minimum allowance of 2,000. Limit
failures return no partial result and carry a diagnostic/span. The copied corpus
qualifies all 652 CommonMark examples with the documented restrictive URL policy,
plus generic extension and adversarial/source preservation cases.

`TypedRenderer` / `Node.to_html()` escape raw HTML by default. Explicit
`trust='trusted'` permits verbatim author HTML; it does not sanitize that HTML.
Default URL permission allows HTTP(S), mailto and safe relative links, rejecting
controls, backslashes, executable schemes and scheme-relative authorities.
Source recognition never grants an unsafe destination permission.

`render(source, dialect=..., context=..., options=...)` returns RenderedMarkdown
with html, headings, languages and diagram metadata. `parse_extended` and
`render_extended` select the built-in extended profile. Document Table is not a
spreadsheet record or persistence value.

RendererContext is immutable and has explicit source_path, trust, dialect and
soft_breaks selections. Optional synchronous callbacks receive:

| Selection | Arguments | Result |
| --- | --- | --- |
| resolver | wiki target, source_path | URL string or None; cached per target/render |
| image_resolver | image name, source_path | URL string or None |
| tag_filter | tag text, source_path | bool indicating visibility |
| decorate_link | destination, source_path | Caller-owned HTML text |
| node_handlers | node, context | Caller-owned HTML text for a registered Node type |

Absent wiki/image resolvers perform no notebook, graph, route, file or network
lookup. Unresolved wiki labels are text; image embeds retain literal syntax.
Local heading fragments can use the generic slugger. Resolved destinations still
pass the default URL policy. Invalid callback results fail without fallback.
Decorators/node handlers own their returned HTML and escaping; selecting them is
an explicit trusted application integration. Handler registrations are copied in
order, require distinct Node types and use the first matching type. No async or
signature injection is inferred.

Legacy component conversion and the optional Python-Markdown backend stay in
Pretty Notebook. Its adoption issue #193 will replace its local generic engine
with compatibility exports and adapters, preserving import paths, wiki/image/tag
policy, trust, tables and metadata. Publication fingerprints must include this
package/version/profile plus adapter/configuration identity. Roll back code and
dependency selection together without changing note source or stored data.

Implementation provenance and fixture notices remain separate in PROVENANCE.md
and the fixture NOTICE. No notebook implementation or fixture data is required
by runtime parsing. The optional Headless Spreadsheets adapter will be selected
by its own issue; the spreadsheet package gains no mandatory parser dependency.
