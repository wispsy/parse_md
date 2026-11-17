from dataclasses import dataclass, FrozenInstanceError
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

import parse_md
from parse_md import COMMONMARK, EXTENDED, Dialect, Node, ParseLimitError, ParseOptions, RendererContext, dialect_identity, parse, render, render_extended


def test_public_exports_exist_and_imports_are_independent():
    assert all(hasattr(parse_md, name) for name in parse_md.__all__)
    program = "import sys, parse_md; assert not {'pretty_notebook','pnbp','markdown','rich','requests','fastapi','pydantic'}.intersection(sys.modules)"
    subprocess.run([sys.executable, '-I', '-c', program], check=True)


def test_complete_attributed_corpus_is_preserved():
    directory = Path(__file__).parent/'fixtures/markdown'
    cases = [item for name in ('commonmark-blocks.json','commonmark-inlines.json') for item in json.loads((directory/name).read_text())]
    assert len(cases) == 652
    assert {item['example'] for item in cases} == set(range(1,653))
    notice = (directory/'NOTICE.md').read_text()
    assert 'John MacFarlane' in notice and 'CC BY-SA 4.0' in notice


def test_versioned_dialects_are_explicit_and_immutable():
    assert dialect_identity(COMMONMARK) == 'commonmark-0.31.2-v1'
    assert dialect_identity('extended') == EXTENDED.identity
    assert '<s>' not in render('~~text~~').html
    assert '<s>text</s>' in render('~~text~~', dialect=EXTENDED).html
    with pytest.raises(FrozenInstanceError):
        COMMONMARK.name = 'other'
    for name in ('other',None):
        with pytest.raises(ValueError):
            parse('text', dialect=name)
    with pytest.raises(ValueError):
        Dialect('extended','2')


def test_resolvers_are_explicit_cached_and_receive_source_path():
    calls = []
    def resolve(target, path):
        calls.append((target,path))
        return '/notes/target' if target == 'Target|Label' else None
    context = RendererContext(source_path='source.md', resolver=resolve,
                              image_resolver=lambda name,path: '/assets/' + name)
    result = render_extended('[[Target|Label]] [[Target|Label]] [[missing|fallback]] ![[image.png]]',context=context)
    assert result.html.count("href='/notes/target'") == 2
    assert calls == [('Target|Label','source.md'),('missing|fallback','source.md')]
    assert 'fallback' in result.html and 'src="/assets/image.png"' in result.html
    assert '[[image.png]]' in render_extended('![[image.png]]').html


def test_application_tag_filter_and_decoration_are_selected_callbacks():
    context=RendererContext(tag_filter=lambda tag,path: tag != '#private',
                            decorate_link=lambda destination,path:'<span>external</span>')
    result=render_extended('#private #topic\n[link](https://example.com)',context=context)
    assert '#private' not in result.html and '#topic' in result.html
    assert '<span>external</span>' in result.html
    assert '<span>external</span>' not in render_extended('[link](https://example.com)').html


@dataclass(frozen=True)
class Badge(Node):
    value: str

    def _markdown(self):
        return ':' + self.value + ':'


def test_custom_node_renderers_are_explicit_and_snapshotted():
    from html import escape
    from parse_md import Document, Paragraph
    handlers={Badge:lambda node, context:'<b>'+escape(node.value)+'</b>'}
    context=RendererContext(node_handlers=handlers)
    handlers.clear()
    document=Document(Paragraph(Badge('<safe>')))
    assert document.to_html(context=context) == '<p><b>&lt;safe&gt;</b></p>'
    with pytest.raises(TypeError):
        document.to_html()
    with pytest.raises(TypeError):
        document.to_html(context=RendererContext(node_handlers={Badge:lambda n,c:42}))


@pytest.mark.parametrize('context', [RendererContext(resolver=lambda target,path:42),
                                    RendererContext(image_resolver=lambda target,path:42),
                                    RendererContext(tag_filter=lambda target,path:42),
                                    RendererContext(decorate_link=lambda target,path:42)])
def test_invalid_callback_results_fail_without_ambient_fallback(context):
    with pytest.raises(TypeError):
        render_extended('[[target]] ![[image.png]] #topic [link](https://example.com)',context=context)


@pytest.mark.parametrize('url', ['javascript:alert(1)','data:text/html,x','https://example.com/\nprivate'])
def test_resolved_urls_retain_safe_html_policy(url):
    result=render_extended('[[target]] ![[image.png]]',context=RendererContext(resolver=lambda t,p:url, image_resolver=lambda t,p:url))
    assert url not in result.html


@pytest.mark.parametrize('source,options', [('x'*101,ParseOptions(max_characters=100)),
                                          ('\n\n'.join(['text']*20),ParseOptions(max_nodes=4)),
                                          ('> '*20+'text',ParseOptions(max_nesting=4))])
def test_common_and_extended_profiles_share_parser_budgets(source,options):
    for dialect in (COMMONMARK,EXTENDED):
        with pytest.raises(ParseLimitError):
            parse(source,dialect=dialect,options=options)


def test_raw_html_requires_explicit_trust_and_exact_source_stays_intact():
    source='<script>private()</script>\r\n\r\n# Héading\r\n'
    document=parse(source)
    assert document.to_markdown() == source
    assert '<script>' not in document.to_html()
    assert '<script>' in document.to_html(context=RendererContext(trust='trusted'))
