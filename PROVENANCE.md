# Source provenance

The engine is extracted from wispsy/pretty-notebook at `4176a490a6cd8708d1ae3afc56bef0fba3bc6132`.
The original extraction inventory records implementation revision
`2bfc586cfce7e982f73cbbb0215c99260388f73c`. The upstream implementation remains
under the retained MIT LICENSE copyright notices.

| Upstream file in src/pretty_notebook/markdown | SHA256 at extraction |
| --- | --- |
| `__init__.py` | `503def524bf5c3dab9788906f9ef1d5bf4d1345859bd9ee45b395e7480091e34` |
| `dialect.py` | `1adfde84f31c7126ef9662f8a2b416b92071010480395d14caf81c99f4228026` |
| `inlines.py` | `b7fde7e08135637fe5c762907c991a0442a0801bd172aedac46767a160a174bb` |
| `nodes.py` | `805668679a71a5d29b9d40eed11557eb3a4133fe39063cd9d57e375d8b80def4` |
| `parser.py` | `927755c99f15b7a6d12fa970312299103f9a57c3cc9dd209d8d626df2dc5771d` |
| `renderers.py` | `246d13e6e750b562a19d62c4f414ca5c6b7c46e573a2ef77aa537bd95ff03059` |

Generic algorithms, source mapping, budgets and corpus data are retained.
NotebookLink becomes WikiLink and the opt-in notebook syntax profile becomes
the generic extended dialect. Notebook/legacy component, routes, graph, icons,
image policy, tag filtering and Python-Markdown imports are replaced by explicit
caller context or retained in the downstream application. No old implementation
has been removed from Pretty Notebook during package qualification; adoption is
tracked by wispsy/pretty-notebook#193 and will replace it with compatibility
imports/adapters rather than maintain two evolving parsers.

The complete CommonMark 0.31.2 fixture data and NOTICE are copied unchanged.
They remain CC BY-SA 4.0, separately from the MIT implementation. Generic tests
are ported from the block/inline/builder/dialect suites; notebook state, legacy
backend and publication tests remain application-owned. Package tests qualify
replacement callback seams without importing Pretty Notebook.
