"""Typed Markdown builders and explicit renderer contexts."""

from .nodes import (
    BlockQuote, BoldText, BulletList, CodeBlock, Document, Heading, Image, ItalicText,
    Link, ListItem, MarkdownText, Node, WikiLink, OrderedList, Paragraph,
    Text, ThematicBreak,
)
from .renderers import Renderer, RendererContext

__all__ = [
    'BoldText', 'BulletList', 'CodeBlock', 'Document', 'Heading', 'Image',
    'ItalicText', 'Link', 'ListItem', 'MarkdownText', 'Node', 'WikiLink',
    'OrderedList', 'Paragraph', 'Text', 
    'Renderer', 'RendererContext',
]

from .parser import Diagnostic, ParseLimitError, ParseOptions, SourceSpan, parse_blocks

__all__ += ["BlockQuote", "ThematicBreak", "Diagnostic", "ParseLimitError", "ParseOptions", "SourceSpan", "parse_blocks"]

from .inlines import parse
from .nodes import Code, HardBreak, RawHtml, ReferenceDefinition, SoftBreak
from .renderers import TypedRenderer

__all__ += ['parse', 'Code', 'HardBreak', 'RawHtml', 'ReferenceDefinition', 'SoftBreak', 'TypedRenderer']

from .dialect import parse_extended
from .nodes import (FootnoteDefinition, FootnoteReference, HighlightedText, ImageEmbed, Mermaid, StrikethroughText, Table, TableCell, TableOfContents, TableRow, TagText, TaskListItem)
from .renderers import (DiagramInfo, HeadingInfo, ExtendedRenderer, RenderedMarkdown, render_extended)

__all__ += ['parse_extended', 'FootnoteDefinition', 'FootnoteReference', 'HighlightedText', 'ImageEmbed', 'Mermaid', 'StrikethroughText', 'Table', 'TableCell', 'TableOfContents', 'TableRow', 'TagText', 'TaskListItem', 'DiagramInfo', 'HeadingInfo', 'ExtendedRenderer', 'RenderedMarkdown', 'render_extended']

from .profiles import COMMONMARK, EXTENDED, Dialect, dialect_identity
from .inlines import parse as _parse
from .parser import parse_blocks as _parse_blocks
from .profiles import select_dialect

__version__ = '0.1.0'

def parse(source, *, dialect=COMMONMARK, options=None):
    return _parse(source, dialect=select_dialect(dialect).name, options=options)

def parse_blocks(source, *, dialect=COMMONMARK, options=None):
    return _parse_blocks(source, dialect=select_dialect(dialect).name, options=options)

def render(source, *, dialect=COMMONMARK, context=None, options=None):
    return TypedRenderer().render_document(parse(source, dialect=dialect, options=options), context)

__all__ += ['COMMONMARK', 'EXTENDED', 'Dialect', 'dialect_identity', 'render', '__version__']
