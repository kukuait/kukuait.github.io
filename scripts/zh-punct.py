#!/usr/bin/env python3
"""
zh-punct.py — Chinese copywriting formatter for MDX files.

Applies pangu spacing (CJK ↔ ASCII gap) and proper-noun casing to plain-text
segments only.  Skips: YAML front-matter, fenced code blocks, inline code,
MDX/JSX expressions, HTML tags, and bare URLs so code and markup are never
touched.

Usage
-----
  # Check what would change (dry-run, prints diff)
  python3 scripts/zh-punct.py content/llm/01-basics/what-is-llm.mdx

  # Apply fixes in-place
  python3 scripts/zh-punct.py --fix content/llm/01-basics/what-is-llm.mdx

  # Exit 1 if any file needs changes (for CI)
  python3 scripts/zh-punct.py --check content/**/*.mdx

  # Via Docker/Podman (no local Python needed)
  docker run --rm -v "$PWD":/work -w /work python:3.12-alpine \\
    sh -c "pip install -q pangu && python3 scripts/zh-punct.py --fix <files>"
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

# ── Dependency check ────────────────────────────────────────────────────────
try:
    import pangu  # pip install pangu
except ImportError:
    sys.exit("Missing dependency: pip install pangu")

# ── Patterns to protect from formatting ─────────────────────────────────────
# Each entry is matched in order; anything inside is passed through unchanged.

_FRONTMATTER = r'(?s:^---\n.*?\n---\n)'            # YAML front-matter (MDX)
_FENCED_CODE  = r'(?s:(?:```|~~~)[^\n]*\n.*?(?:```|~~~))'  # ``` or ~~~
_MDX_EXPR     = r'\{[^}]*\}'                        # {expr} / {/* comment */}
_HTML_TAG     = r'<[^>\n]+/?>'                      # <Tag />, <br/>, </Tag>
_INLINE_CODE  = r'`[^`\n]+`'                        # `code`
_URL          = r'https?://\S+'                     # bare URLs

# Compiled splitter: keeps protected spans as captured groups so re.split
# returns [text, protected, text, protected, ...].
_PROTECT_RE = re.compile(
    '(' + '|'.join([
        _FRONTMATTER,
        _FENCED_CODE,
        _MDX_EXPR,
        _HTML_TAG,
        _INLINE_CODE,
        _URL,
    ]) + ')',
    re.MULTILINE,
)

# Markdown links: format the display text, leave the URL untouched.
_LINK_RE = re.compile(r'\[([^\]\n]*)\]\(([^)\n]*)\)')

# ── Proper-noun table ────────────────────────────────────────────────────────
# Add entries as (compiled-pattern, replacement).  \b anchors prevent partial
# matches inside longer words or URLs (URLs are already protected above).
_PROPER_NOUNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r'\bjson\b',  re.I), 'JSON'),
    (re.compile(r'\bapi\b',   re.I), 'API'),
    (re.compile(r'\burl\b',   re.I), 'URL'),
    (re.compile(r'\bhtml\b',  re.I), 'HTML'),
    (re.compile(r'\bcss\b',   re.I), 'CSS'),
    (re.compile(r'\bhttp\b',  re.I), 'HTTP'),
    (re.compile(r'\bhttps\b', re.I), 'HTTPS'),
    (re.compile(r'\bllm\b',   re.I), 'LLM'),
    (re.compile(r'\bllms\b',  re.I), 'LLMs'),
    (re.compile(r'\brag\b',   re.I), 'RAG'),
    (re.compile(r'\bslo\b',   re.I), 'SLO'),
    (re.compile(r'\bsli\b',   re.I), 'SLI'),
    (re.compile(r'\bsre\b',   re.I), 'SRE'),
    (re.compile(r'\bgpu\b',   re.I), 'GPU'),
    (re.compile(r'\bcpu\b',   re.I), 'CPU'),
    (re.compile(r'\boop\b',   re.I), 'OOP'),
    (re.compile(r'\bci/cd\b', re.I), 'CI/CD'),
    (re.compile(r'\bsql\b',   re.I), 'SQL'),
    (re.compile(r'\bnosql\b', re.I), 'NoSQL'),
    (re.compile(r'\bgrpc\b',  re.I), 'gRPC'),
    (re.compile(r'\brest\b',  re.I), 'REST'),
    (re.compile(r'\bgit\b',   re.I), 'Git'),
    (re.compile(r'\bgithub\b',re.I), 'GitHub'),
]

# ── Inline markdown protection ───────────────────────────────────────────────
# pangu adds spaces between `*` (ASCII) and CJK, which breaks **bold** syntax.
# Protect inline formatting spans with PUA placeholders before pangu runs so
# the bold/italic markers are never seen as CJK↔ASCII boundaries.
# PUA characters (U+E000–) are not in pangu's half-width ASCII target range,
# so they won't trigger spurious spacing themselves.

_INLINE_MD_RE = re.compile(
    r'\*{3}[^*\n]+\*{3}'   # ***bold-italic***
    r'|\*{2}[^*\n]+\*{2}'  # **bold**
    r'|\*[^*\n]+\*'         # *italic*
    r'|_{2}[^_\n]+_{2}'    # __bold__
    r'|_[^_\n]+_'           # _italic_
    r'|~{2}[^~\n]+~{2}'    # ~~strikethrough~~
)

# ── Core formatting ──────────────────────────────────────────────────────────

def _apply_proper_nouns(text: str) -> str:
    for pat, repl in _PROPER_NOUNS:
        text = pat.sub(repl, text)
    return text

def _format_plain(text: str) -> str:
    """
    Apply pangu + proper nouns to plain text.

    Two invariants maintained:
    1. Leading/trailing whitespace (newlines, spaces) is preserved verbatim —
       pangu strips them internally, so we peel them off and re-attach.
    2. Inline markdown spans (**, *, __, ~~) are hidden from pangu via PUA
       placeholders so their markers are never treated as CJK↔ASCII boundaries.
    """
    # Peel off leading/trailing whitespace that pangu would strip
    core = text.strip('\n ')
    if not core:
        return text
    lead  = text[:len(text) - len(text.lstrip('\n '))]
    trail = text[len(text.rstrip('\n ')):]

    # Protect inline MD on each line (line-by-line also avoids pangu
    # collapsing multi-line plain segments across blank-line boundaries)
    result_lines: list[str] = []
    for line in core.split('\n'):
        placeholders: dict[str, str] = {}
        idx = [0]

        def _protect(m: re.Match) -> str:
            key = f'{idx[0]}'
            placeholders[key] = m.group(0)
            idx[0] += 1
            return key

        protected = _INLINE_MD_RE.sub(_protect, line)
        formatted  = pangu.spacing(protected)
        formatted  = _apply_proper_nouns(formatted)
        for k, v in placeholders.items():
            formatted = formatted.replace(k, v)
        result_lines.append(formatted)

    return lead + '\n'.join(result_lines) + trail

def _format_segment(segment: str) -> str:
    """
    Format one plain-text segment.

    Links ([text](url)) need special care: the display text is formatted but
    the URL must be left untouched.  We protect each link with a PUA placeholder
    BEFORE _format_plain runs (so proper-noun rules never fire on a URL), then
    restore the final link with the formatted display text and original URL.
    """
    link_cache: dict[str, str] = {}
    idx = [0]

    def _protect_link(m: re.Match) -> str:
        display = _format_plain(m.group(1))   # format display text only
        key = f'{idx[0]}'
        link_cache[key] = f'[{display}]({m.group(2)})'
        idx[0] += 1
        return key

    protected = _LINK_RE.sub(_protect_link, segment)
    result    = _format_plain(protected)
    for k, v in link_cache.items():
        result = result.replace(k, v)
    return result

def format_content(content: str) -> str:
    """
    Split content into protected and plain-text alternating spans, apply
    formatting only to plain-text spans, then reassemble.
    """
    parts = _PROTECT_RE.split(content)
    # re.split with a capturing group returns:
    #   [plain, protected, plain, protected, ..., plain]
    # i.e. even indices → plain text, odd indices → protected
    out: list[str] = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            out.append(_format_segment(part))
        else:
            out.append(part)   # protected: pass through verbatim
    return ''.join(out)

# ── File handling ────────────────────────────────────────────────────────────

def process_file(path: Path, *, fix: bool, check: bool) -> bool:
    """
    Process one file.  Returns True if the file would change (or was changed).
    """
    original = path.read_text(encoding='utf-8')
    formatted = format_content(original)

    if formatted == original:
        return False  # nothing to do

    if check:
        print(f'[would change] {path}')
        return True

    if fix:
        path.write_text(formatted, encoding='utf-8')
        print(f'[fixed] {path}')
        return True

    # Dry-run: print unified diff
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        formatted.splitlines(keepends=True),
        fromfile=str(path),
        tofile=str(path) + ' (formatted)',
    )
    sys.stdout.writelines(diff)
    return True

# ── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description='Chinese copywriting formatter for MDX files.',
    )
    parser.add_argument('files', nargs='+', type=Path, help='MDX/MD files to process')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--fix',   action='store_true', help='Write changes in-place')
    mode.add_argument('--check', action='store_true', help='Exit 1 if any file needs changes')
    args = parser.parse_args()

    any_changed = False
    for path in args.files:
        if not path.exists():
            print(f'[skip] {path} not found', file=sys.stderr)
            continue
        changed = process_file(path, fix=args.fix, check=args.check)
        any_changed = any_changed or changed

    if args.check and any_changed:
        sys.exit(1)

if __name__ == '__main__':
    main()
