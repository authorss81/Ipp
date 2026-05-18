"""
ipp/runtime/highlighter.py
v1.7.9.1.5 — REPL Syntax Highlighting

Provides live syntax highlighting for the Ipp REPL using prompt_toolkit.
Falls back gracefully to plain input() when prompt_toolkit is unavailable.

Architecture:
  IppLexer         — pygments-compatible token stream for Ipp source
  IppHighlighter   — prompt_toolkit Lexer that feeds IppLexer
  IppCompleter     — context-aware tab completion
  HighlightSession — drop-in replacement for input() with full features
"""

from __future__ import annotations
import re
from typing import Optional, Callable

# ── Token categories ──────────────────────────────────────────────────────────
_KW = frozenset({
    'func', 'class', 'var', 'let', 'const', 'if', 'elif', 'else',
    'for', 'while', 'do', 'until', 'return', 'break', 'continue',
    'import', 'from', 'as', 'try', 'catch', 'throw', 'finally',
    'match', 'case', 'default', 'async', 'await', 'yield',
    'extends', 'super', 'self', 'this', 'new', 'in', 'not', 'and',
    'or', 'is', 'enum', 'interface', 'implements', 'static',
    'pub', 'priv', 'mut', 'ref', 'defer', 'with', 'pass', 'del',
})
_ATOM = frozenset({'nil', 'true', 'false'})
_BUILTIN = frozenset({
    'print', 'str', 'int', 'float', 'bool', 'len', 'abs', 'type',
    'range', 'assert', 'list', 'dict', 'set', 'tuple', 'max', 'min',
    'sum', 'sorted', 'reversed', 'enumerate', 'zip', 'map', 'filter',
    'input', 'chr', 'ord', 'hex', 'bin', 'oct', 'repr', 'hash', 'id',
    'dir', 'vars', 'callable', 'hasattr', 'getattr', 'setattr',
    'isinstance', 'issubclass', 'iter', 'next', 'open', 'round',
    'pow', 'divmod', 'all', 'any', 'slice', 'eval',
    'ipp_type', 'ipp_version', 'strip_ansi', 'json_parse',
    'json_stringify', 'base64_encode', 'base64_decode',
    'key_pressed', 'get_key', 'get_key_async', 'on_keydown',
    'on_keyup', 'advance_frame', 'simulate_key_press',
    'simulate_key_release', 'KEY',
    'vec2', 'vec3', 'vec4', 'mat4', 'quat', 'complex', 'Color',
    'Rect', 'Vector2', 'Vector3', 'Signal', 'deque', 'datetime',
    'sqrt', 'sin', 'cos', 'tan', 'atan2', 'floor', 'ceil', 'log',
    'exp', 'pi', 'tau', 'inf', 'random', 'randint', 'choice',
    'shuffle', 'seed', 'async_run', 'format', 'sprintf',
    'canvas', 'scene', 'node', 'camera', 'mesh', 'light',
    'http_get', 'http_post', 'logger',
})
_TYPE = frozenset({
    'Number', 'String', 'Bool', 'List', 'Dict', 'Set', 'Func',
    'Class', 'Object', 'Vector2', 'Vector3', 'Vector4', 'Matrix4',
    'Quaternion', 'Color', 'Rect', 'Complex', 'Signal',
    'Error', 'TypeError', 'ValueError', 'IndexError', 'KeyError',
    'RuntimeError', 'ZeroDivisionError',
})

# ── Token types (string tags) ─────────────────────────────────────────────────
TK_KW       = 'keyword'
TK_ATOM     = 'atom'
TK_BUILTIN  = 'builtin'
TK_TYPE     = 'type'
TK_STRING   = 'string'
TK_NUMBER   = 'number'
TK_COMMENT  = 'comment'
TK_OP       = 'operator'
TK_PUNCT    = 'punctuation'
TK_IDENT    = 'ident'
TK_FUNC_DEF = 'func_def'   # identifier right after 'func'
TK_CLASS_DEF= 'class_def'  # identifier right after 'class'
TK_CALL     = 'call'       # identifier followed by '('
TK_DECO     = 'decorator'  # @name
TK_PLAIN    = 'plain'


def tokenize_line(src: str) -> list[tuple[str, str]]:
    """
    Tokenise a single line of Ipp source into (token_type, text) pairs.
    Returns a flat list — used by the prompt_toolkit highlighter.
    """
    tokens = []
    i = 0
    n = len(src)
    prev_kw = None  # track 'func'/'class' to highlight the next identifier

    while i < n:
        c = src[i]

        # Whitespace
        if c in ' \t':
            tokens.append((TK_PLAIN, c))
            i += 1
            continue

        # Comment: # to end of line
        if c == '#':
            tokens.append((TK_COMMENT, src[i:]))
            break

        # String: single or double quoted, with escape support
        if c in ('"', "'"):
            j = i + 1
            while j < n:
                if src[j] == '\\':
                    j += 2
                    continue
                if src[j] == c:
                    j += 1
                    break
                j += 1
            tokens.append((TK_STRING, src[i:j]))
            i = j
            continue

        # Decorator: @identifier
        if c == '@' and i + 1 < n and (src[i+1].isalpha() or src[i+1] == '_'):
            j = i + 1
            while j < n and (src[j].isalnum() or src[j] == '_'):
                j += 1
            tokens.append((TK_DECO, src[i:j]))
            i = j
            continue

        # Number: hex, float, int
        if c.isdigit() or (c == '0' and i+1 < n and src[i+1] in 'xXbBoO'):
            j = i
            if src[j:j+2].lower() in ('0x', '0b', '0o'):
                j += 2
                while j < n and (src[j].isalnum() or src[j] == '_'):
                    j += 1
            else:
                while j < n and (src[j].isdigit() or src[j] in '._eE'):
                    if src[j] in 'eE' and j+1 < n and src[j+1] in '+-':
                        j += 2
                    else:
                        j += 1
            tokens.append((TK_NUMBER, src[i:j]))
            i = j
            continue

        # Identifier or keyword
        if c.isalpha() or c == '_':
            j = i
            while j < n and (src[j].isalnum() or src[j] == '_'):
                j += 1
            word = src[i:j]

            # Determine token type
            if word in _KW:
                tokens.append((TK_KW, word))
                prev_kw = word
            elif word in _ATOM:
                tokens.append((TK_ATOM, word))
                prev_kw = None
            elif prev_kw == 'func':
                tokens.append((TK_FUNC_DEF, word))
                prev_kw = None
            elif prev_kw == 'class':
                tokens.append((TK_CLASS_DEF, word))
                prev_kw = None
            elif word in _TYPE:
                tokens.append((TK_TYPE, word))
                prev_kw = None
            elif word in _BUILTIN:
                # Check if followed by '(' → call
                k = j
                while k < n and src[k] == ' ':
                    k += 1
                tokens.append((TK_BUILTIN, word))
                prev_kw = None
            else:
                # Check if followed by '(' → call
                k = j
                while k < n and src[k] == ' ':
                    k += 1
                if k < n and src[k] == '(':
                    tokens.append((TK_CALL, word))
                else:
                    tokens.append((TK_IDENT, word))
                prev_kw = None
            i = j
            continue

        # Multi-char operators: ==, !=, <=, >=, ->, =>, .., ...
        if c in '!<>=+-*/%&|^~.':
            two   = src[i:i+2]
            three = src[i:i+3]
            if three in ('...', '<<=', '>>='):
                tokens.append((TK_OP, three)); i += 3
            elif two in ('==', '!=', '<=', '>=', '->', '=>', '**',
                         '//', '<<', '>>', '+=', '-=', '*=', '/=',
                         '%=', '&=', '|=', '^=', '..'):
                tokens.append((TK_OP, two)); i += 2
            else:
                tokens.append((TK_OP, c)); i += 1
            continue

        # Brackets / punctuation
        if c in '(){}[],:;':
            tokens.append((TK_PUNCT, c))
            i += 1
            continue

        # Anything else
        tokens.append((TK_PLAIN, c))
        i += 1

    return tokens


# ── prompt_toolkit integration ────────────────────────────────────────────────
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.lexers import Lexer as PTLexer
    from prompt_toolkit.styles import Style
    from prompt_toolkit.formatted_text import FormattedText
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.history import InMemoryHistory, FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.filters import has_completions, completion_is_selected
    _HAS_PT = True
except ImportError:
    _HAS_PT = False


# ── Colour themes for the REPL input line ────────────────────────────────────
_THEMES: dict[str, dict] = {
    'default': {
        TK_KW:        '#c878ff bold',   # bright purple — very visible
        TK_ATOM:      '#ff9f5e bold',   # warm orange   — nil/true/false stand out
        TK_BUILTIN:   '#5ec8ff',        # bright cyan   — easy to spot
        TK_TYPE:      '#ffd060 bold',   # golden yellow — type names
        TK_STRING:    '#5edc96',        # vivid green   — strings always readable
        TK_NUMBER:    '#ffcc44',        # clear yellow  — numbers
        TK_COMMENT:   '#606880 italic', # muted blue-grey — not intrusive
        TK_OP:        '#ff9f5e',        # warm orange   — operators
        TK_PUNCT:     '#7888b0',        # mid blue-grey — braces/parens
        TK_IDENT:     '#d8dcf0',        # near-white    — plain identifiers
        TK_FUNC_DEF:  '#62b8ff bold',   # sky blue bold — func name after 'func'
        TK_CLASS_DEF: '#ffd060 bold',   # golden bold   — class name after 'class'
        TK_CALL:      '#62b8ff',        # sky blue      — function calls
        TK_DECO:      '#c878ff',        # purple        — @decorators
        TK_PLAIN:     '#d8dcf0',        # near-white
    },
    'dracula': {
        TK_KW:        '#ff79c6 bold',
        TK_ATOM:      '#bd93f9',
        TK_BUILTIN:   '#8be9fd',
        TK_TYPE:      '#ffb86c bold',
        TK_STRING:    '#f1fa8c',
        TK_NUMBER:    '#bd93f9',
        TK_COMMENT:   '#6272a4 italic',
        TK_OP:        '#ff79c6',
        TK_PUNCT:     '#f8f8f2',
        TK_IDENT:     '#f8f8f2',
        TK_FUNC_DEF:  '#50fa7b bold',
        TK_CLASS_DEF: '#ffb86c bold',
        TK_CALL:      '#8be9fd',
        TK_DECO:      '#ff79c6',
        TK_PLAIN:     '#f8f8f2',
    },
    'monokai': {
        TK_KW:        '#f92672 bold',
        TK_ATOM:      '#ae81ff',
        TK_BUILTIN:   '#66d9e8',
        TK_TYPE:      '#fd971f bold',
        TK_STRING:    '#e6db74',
        TK_NUMBER:    '#ae81ff',
        TK_COMMENT:   '#75715e italic',
        TK_OP:        '#f92672',
        TK_PUNCT:     '#f8f8f2',
        TK_IDENT:     '#f8f8f2',
        TK_FUNC_DEF:  '#a6e22e bold',
        TK_CLASS_DEF: '#fd971f bold',
        TK_CALL:      '#a6e22e',
        TK_DECO:      '#f92672',
        TK_PLAIN:     '#f8f8f2',
    },
    'solarized': {
        TK_KW:        '#268bd2 bold',
        TK_ATOM:      '#d33682',
        TK_BUILTIN:   '#2aa198',
        TK_TYPE:      '#b58900 bold',
        TK_STRING:    '#859900',
        TK_NUMBER:    '#d33682',
        TK_COMMENT:   '#657b83 italic',
        TK_OP:        '#cb4b16',
        TK_PUNCT:     '#839496',
        TK_IDENT:     '#93a1a1',
        TK_FUNC_DEF:  '#268bd2 bold',
        TK_CLASS_DEF: '#b58900 bold',
        TK_CALL:      '#268bd2',
        TK_DECO:      '#6c71c4',
        TK_PLAIN:     '#839496',
    },
    'nord': {
        TK_KW:        '#81a1c1 bold',
        TK_ATOM:      '#b48ead',
        TK_BUILTIN:   '#88c0d0',
        TK_TYPE:      '#ebcb8b bold',
        TK_STRING:    '#a3be8c',
        TK_NUMBER:    '#b48ead',
        TK_COMMENT:   '#4c566a italic',
        TK_OP:        '#81a1c1',
        TK_PUNCT:     '#d8dee9',
        TK_IDENT:     '#e5e9f0',
        TK_FUNC_DEF:  '#88c0d0 bold',
        TK_CLASS_DEF: '#ebcb8b bold',
        TK_CALL:      '#88c0d0',
        TK_DECO:      '#b48ead',
        TK_PLAIN:     '#e5e9f0',
    },
    'gruvbox': {
        TK_KW:        '#fb4934 bold',
        TK_ATOM:      '#d3869b',
        TK_BUILTIN:   '#83a598',
        TK_TYPE:      '#fabd2f bold',
        TK_STRING:    '#b8bb26',
        TK_NUMBER:    '#d3869b',
        TK_COMMENT:   '#928374 italic',
        TK_OP:        '#fe8019',
        TK_PUNCT:     '#ebdbb2',
        TK_IDENT:     '#ebdbb2',
        TK_FUNC_DEF:  '#8ec07c bold',
        TK_CLASS_DEF: '#fabd2f bold',
        TK_CALL:      '#8ec07c',
        TK_DECO:      '#d3869b',
        TK_PLAIN:     '#ebdbb2',
    },
}

_current_theme_name: str = 'default'


def set_highlight_theme(name: str) -> bool:
    global _current_theme_name
    if name in _THEMES:
        _current_theme_name = name
        return True
    return False


def _make_pt_style(theme_name: str) -> 'Style':
    """Build a prompt_toolkit Style from a theme dict."""
    theme = _THEMES.get(theme_name, _THEMES['default'])
    mapping = {}
    for tok, css in theme.items():
        mapping[f'class:{tok}'] = css
    # Prompt style
    mapping['class:prompt']     = '#7eb3ff bold'
    mapping['class:prompt_cont']= '#4f5577'
    return Style.from_dict(mapping)


if _HAS_PT:
    class _IppPTLexer(PTLexer):
        """prompt_toolkit Lexer that uses tokenize_line."""
        def lex_document(self, document):
            def get_tokens(line_no):
                line = document.lines[line_no] if line_no < len(document.lines) else ''
                raw = tokenize_line(line)
                return [(f'class:{tt}', text) for tt, text in raw]
            return get_tokens

    class _IppCompleter(Completer):
        """Context-aware completer: keywords + builtins + user symbols."""
        def __init__(self):
            self._user_symbols: list[str] = []

        def update_symbols(self, symbols: list[str]):
            self._user_symbols = symbols

        def get_completions(self, document, complete_event):
            word = document.get_word_before_cursor(pattern=re.compile(r'[a-zA-Z_]\w*'))
            if not word:
                return
            candidates = sorted(
                set(_KW) | set(_ATOM) | set(_BUILTIN) | set(_TYPE)
                | set(self._user_symbols)
            )
            for c in candidates:
                if c.startswith(word) and c != word:
                    # Show category in meta
                    if c in _KW:       meta = 'keyword'
                    elif c in _ATOM:   meta = 'literal'
                    elif c in _BUILTIN:meta = 'builtin'
                    elif c in _TYPE:   meta = 'type'
                    else:              meta = 'symbol'
                    yield Completion(c, start_position=-len(word),
                                     display_meta=meta)


class HighlightSession:
    """
    Drop-in replacement for raw input() that adds:
      • Syntax highlighting as you type (prompt_toolkit)
      • Smart tab completion with categories
      • History (persistent file or in-memory)
      • Auto-suggest from history (grey ghost text)
      • Bracket/quote matching indicator
      • Ctrl+C / Ctrl+D handling
      • Graceful fallback to plain input() if prompt_toolkit is absent
    """

    def __init__(self, history_file: Optional[str] = None):
        self._completer = None
        self._session   = None
        self._theme     = _current_theme_name

        if not _HAS_PT:
            return

        self._completer = _IppCompleter()

        hist = FileHistory(history_file) if history_file else InMemoryHistory()

        kb = KeyBindings()

        @kb.add('tab', filter=~has_completions)
        def _(event):
            event.current_buffer.start_completion(select_first=False)

        @kb.add('enter', filter=completion_is_selected)
        def _(event):
            event.current_buffer.complete_state = None

        self._session = PromptSession(
            lexer=_IppPTLexer(),
            completer=self._completer,
            style=_make_pt_style(self._theme),
            history=hist,
            auto_suggest=AutoSuggestFromHistory(),
            key_bindings=kb,
            include_default_pygments_style=False,
            multiline=False,
            enable_history_search=True,
            complete_while_typing=False,  # only on Tab
            mouse_support=False,
        )

    def set_theme(self, name: str):
        """Switch highlight theme at runtime."""
        global _current_theme_name
        if set_highlight_theme(name) and self._session:
            self._theme = name
            self._session.style = _make_pt_style(name)

    def update_symbols(self, symbols: list[str]):
        """Refresh user-defined symbols for completion."""
        if self._completer:
            self._completer.update_symbols(symbols)

    def prompt(self, prompt_text: str, continuation: bool = False) -> str:
        """
        Read one line with highlighting. Returns the raw string.
        Raises EOFError on Ctrl+D, KeyboardInterrupt on Ctrl+C.
        """
        if not _HAS_PT or self._session is None:
            return input(prompt_text)

        # Strip ANSI from prompt for prompt_toolkit (it uses its own styling)
        clean = re.sub(r'\033\[[0-9;]*m', '', prompt_text)

        # Format as FormattedText so the prompt itself is coloured
        cls = 'class:prompt_cont' if continuation else 'class:prompt'
        pt_prompt = FormattedText([(cls, clean)])

        return self._session.prompt(pt_prompt)

    @property
    def available(self) -> bool:
        return _HAS_PT and self._session is not None


def make_session(history_file: Optional[str] = None) -> HighlightSession:
    """Factory — call once and reuse the session."""
    return HighlightSession(history_file=history_file)


def highlight_line(src: str, theme: str = 'default') -> str:
    """
    Render a source line as an ANSI-coloured string for display in the REPL
    (e.g. for showing last input, error snippets, .edit output).
    Uses 24-bit RGB colour codes.
    """
    theme_data = _THEMES.get(theme, _THEMES['default'])
    # Convert CSS hex colours to ANSI RGB
    buf = []
    for tok_type, text in tokenize_line(src):
        css = theme_data.get(tok_type, '')
        m = re.search(r'#([0-9a-fA-F]{6})', css)
        if m:
            r = int(m.group(1)[0:2], 16)
            g = int(m.group(1)[2:4], 16)
            b = int(m.group(1)[4:6], 16)
            bold = ' bold' in css
            ansi = f'\033[38;2;{r};{g};{b}m'
            if bold:
                ansi = '\033[1m' + ansi
            buf.append(ansi + text + '\033[0m')
        else:
            buf.append(text)
    return ''.join(buf)
