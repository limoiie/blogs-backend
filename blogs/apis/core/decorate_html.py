import re

import bs4

pandoc_languages = [
    'actionscript', 'ada', 'agda', 'apache', 'asn1', 'asp', 'ats', 'awk',
    'bash', 'bibtex', 'boo', 'c', 'changelog', 'clojure', 'cmake', 'coffee',
    'coldfusion', 'comments', 'commonlisp', 'cpp', 'cs', 'css', 'curry', 'd',
    'default', 'diff', 'djangotemplate', 'dockerfile', 'dot', 'doxygen',
    'doxygenlua', 'dtd', 'eiffel', 'elixir', 'elm', 'email', 'erlang', 'fasm',
    'fortranfixed', 'fortranfree', 'fsharp', 'gcc', 'glsl', 'gnuassembler',
    'go', 'graphql', 'groovy', 'hamlet', 'haskell', 'haxe', 'html', 'idris',
    'ini', 'isocpp', 'j', 'java', 'javadoc', 'javascript', 'javascriptreact',
    'json', 'jsp', 'julia', 'kotlin', 'latex', 'lex', 'lilypond',
    'literatecurry', 'literatehaskell', 'llvm', 'lua', 'm4', 'makefile',
    'mandoc', 'markdown', 'mathematica', 'matlab', 'maxima', 'mediawiki',
    'metafont', 'mips', 'modelines', 'modula2', 'modula3', 'monobasic',
    'mustache', 'nasm', 'nim', 'noweb', 'objectivec', 'objectivecpp', 'ocaml',
    'octave', 'opencl', 'pascal', 'perl', 'php', 'pike', 'postscript', 'povray',
    'powershell', 'prolog', 'protobuf', 'pure', 'purebasic', 'python', 'qml',
    'r', 'raku', 'relaxng', 'relaxngcompact', 'rest', 'rhtml', 'roff', 'ruby',
    'rust', 'scala', 'scheme', 'sci', 'sed', 'sgml', 'sml', 'spdxcomments',
    'sql', 'sqlmysql', 'sqlpostgresql', 'stata', 'swift', 'tcl', 'tcsh',
    'texinfo', 'toml', 'typescript', 'verilog', 'vhdl', 'xml', 'xorg', 'xslt',
    'xul', 'yacc', 'yaml', 'zsh', 'yara', 'example'
]

map_language_from_pandoc_to_prism = {
    'elisp': 'commonlisp',
}


def decorate_html(html: bytes):
    html_dom = bs4.BeautifulSoup(html, 'html.parser')
    _make_header_as_link(html_dom)
    _decorate_prism_code(html_dom)
    return html_dom.encode()


def _make_header_as_link(html_tag: bs4.BeautifulSoup):
    for header_tag in html_tag.find_all(['h2', 'h3']):
        if 'id' not in header_tag.attrs:
            header_tag.attrs['id'] = to_html_tag_id(header_tag.text)

        children_iter = header_tag.children
        inner_tag = next(children_iter)
        if inner_tag.name == 'a':
            continue

        tag_id = header_tag.attrs['id']
        a_tag = html_tag.new_tag('a', attrs={'href': f'#{tag_id}'})
        inner_tag.wrap(a_tag)
        for child_tag in children_iter:
            a_tag.append(child_tag)

    return html_tag


def _decorate_prism_code(html_tag: bs4.BeautifulSoup):
    """
    Decorate code block in prism format.

    :param html_tag: The html dom
    :return: Decorated html dom
    """
    def to_prism_cls(cls):
        if cls not in pandoc_languages:
            return None
        if cls in map_language_from_pandoc_to_prism:
            cls = map_language_from_pandoc_to_prism[cls]
        return 'language-' + cls

    for code_tag in html_tag.select('pre code'):
        pre_tag = code_tag.parent
        if 'class' not in pre_tag.attrs:
            continue
        if 'class' not in code_tag.attrs:
            code_tag.attrs['class'] = []
        for prism_cls in map(to_prism_cls, pre_tag.attrs['class']):
            if prism_cls is not None:
                pre_tag.attrs['class'].append(prism_cls)
                code_tag.attrs['class'].append(prism_cls)

    return html_tag


def to_html_tag_id(text: bytes):
    return re.sub(b'[^a-zA-Z0-9._-]', b'', text)
