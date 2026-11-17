import html

import pytest

from parse_md import (
    FootnoteDefinition, ImageEmbed, Mermaid, WikiLink, RendererContext,
    StrikethroughText, Table, TagText, TaskListItem, parse, parse_extended, render_extended,
)


def _walk(node):
    yield node
    for child in getattr(node, 'children', ()):
        yield from _walk(child)


def test_dialect_is_explicit_and_preserves_original_source():
    source = '# Heading {#custom}\r\n\r\n~~one~~ ==two== [[wiki]] ![[image.png]] #topic\r\n'
    document = parse_extended(source)
    assert document.to_markdown() == source
    kinds = {type(node) for node in _walk(document)}
    assert {StrikethroughText, WikiLink, ImageEmbed, TagText} <= kinds
    assert '<s>' not in parse(source).to_html()
    assert render_extended(source).headings[0].identifier == 'custom'


def test_nested_formatting_and_comparisons():
    rendered = render_extended('~~one **strong**~~ and ~~two~~\n==three *em*== and ==four==\nplain x == y == z').html
    assert '<s>one <strong>strong</strong></s> and <s>two</s>' in rendered
    assert '<mark>three <em>em</em></mark> and <mark>four</mark>' in rendered
    assert 'plain x == y == z' in rendered


def test_tables_alignment_escaped_pipes_padding_and_inline_code():
    source = '| A | B |\n| :--- | ---: |\n| a\\|b | `x|y` |\n| only |\n'
    document = parse_extended(source)
    assert isinstance(document.children[0], Table)
    rendered = document.to_html()
    assert '<th style="text-align: left;">A</th>' in rendered
    assert '<td style="text-align: right;"><code>x|y</code></td>' in rendered
    assert 'a|b' in rendered and '<td style="text-align: right;"></td>' in rendered
    assert document.to_markdown() == source


def test_nested_tasks_have_typed_state_and_disabled_checkboxes():
    source = '- [ ] first\n  - [x] nested\n- [X] done\n'
    document = parse_extended(source)
    tasks = [node for node in _walk(document) if isinstance(node, TaskListItem)]
    assert [task.checked for task in tasks] == [False, True, True]
    rendered = document.to_html()
    assert rendered.count('disabled=""') == 3 and rendered.count('checked=""') == 2
    assert document.to_markdown() == source


def test_footnotes_have_multiple_backlinks_and_block_content():
    source = 'Text[^one] again[^one] and [^missing].\n\n[^one]: A **footnote**.\n\n    Another paragraph.\n'
    document = parse_extended(source)
    assert isinstance(document.children[1], FootnoteDefinition)
    rendered = document.to_html()
    assert 'id="fnref:one"' in rendered and 'id="fnref2:one"' in rendered
    assert rendered.count('class="footnote-backref"') == 2
    assert '<p>Another paragraph.' in rendered and '[^missing]' in rendered
    assert document.to_markdown() == source


def test_attributes_heading_ids_toc_and_metadata_share_anchors():
    source = '# Héading\n## Repeat\n## Repeat\n## Custom {: #read .chapter onclick="bad"}\n\n[TOC]\n\n[link](/safe){: .reference title="A &quot; title"}\n'
    result = render_extended(source)
    assert [heading.identifier for heading in result.headings] == ['heading', 'repeat', 'repeat_1', 'read']
    for heading in result.headings:
        assert f'id="{heading.identifier}"' in result.html
        assert f'href="#{heading.identifier}"' in result.html
    assert 'onclick' not in result.html and 'class="chapter"' in result.html
    assert 'class="reference"' in result.html and 'title="A &quot; title"' in result.html


def test_attributes_cannot_inject_attributes_or_executable_urls():
    source = '## Safe {#safe onmouseover="bad" style="color:red"}\n\n![alt](javascript:bad){: onerror="bad" data-label="&quot;"}\n'
    rendered = render_extended(source).html
    assert 'onmouseover=' not in rendered and 'onerror=' not in rendered and 'style=' not in rendered
    assert 'src=""' in rendered and 'data-label="&quot;"' in rendered


def test_mermaid_and_code_metadata_are_structured_and_literal():
    body = '\t[[wiki]] #tag <script> ==literal==\n'
    source = f'```mermaid\n{body}```\n\n```{{.python #sample .extra}}\nprint(1)\n```\n'
    document = parse_extended(source)
    assert isinstance(document.children[0], Mermaid)
    result = render_extended(source)
    assert result.languages == ('mermaid', 'python')
    assert result.diagrams[0].source == body
    assert '<pre class="mermaid">' in result.html and '<script>' not in result.html
    assert '<pre class="extra" id="sample"><code class="language-python">' in result.html
    assert body in html.unescape(result.html)






@pytest.mark.parametrize('literal', [
    '`[[Target]] #public ~~strike~~ ==mark== https://example.com`',
    '```text\n[[Target]] #public ~~strike~~ ==mark== https://example.com\n```',
    '    [[Target]] #public ~~strike~~ ==mark== https://example.com\n',
    '```mermaid\n[[Target]] #public ~~strike~~ ==mark== https://example.com\n```',
    '<pre>[[Target]] #public ~~strike~~ ==mark== https://example.com</pre>',
    'Before <code>[[Target]] #public ~~strike~~ ==mark== https://example.com</code> after',
])
def test_extensions_leave_protected_text_opaque(literal):
    result = render_extended(literal, context=RendererContext(source_path='Source.md', trust='trusted'))
    assert '<a ' not in result.html and '<s>' not in result.html and '<mark>' not in result.html
    assert '[[Target]] #public ~~strike~~ ==mark== https://example.com' in html.unescape(result.html)




def test_attribute_titles_override_existing_titles_once():
    rendered = render_extended('[x](/safe "old"){: title="new"} ![x](/image "old"){: title="new"}').html
    assert rendered.count('title="new"') == 2
    assert 'title="old"' not in rendered


def test_duplicate_footnote_definitions_use_the_first_body():
    rendered = render_extended('Text[^a].\n\n[^a]: first\n\n[^a]: second\n').html
    assert '<p>first' in rendered and '<p>second' not in rendered


def test_opaque_html_code_keeps_visible_heading_text_for_anchors():
    result = render_extended('# Before <code>[[literal]]</code> after\n', context=RendererContext(trust='trusted'))
    assert result.headings[0].title == 'Before [[literal]] after'
    assert result.headings[0].identifier == 'before-literal-after'
    assert '<code>[[literal]]</code>' in result.html
