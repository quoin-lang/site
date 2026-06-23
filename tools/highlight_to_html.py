#!/usr/bin/env python3
"""Turn a Quoin snippet into the HTML used in this site's <pre> code blocks.

The site renders Quoin code with hand-spanned syntax highlighting whose colors
match the language's own highlighter (`qn highlight`). Rather than tint code by
hand, write the snippet as plain Quoin and run it through this tool: it shells
out to `qn highlight`, then converts the truecolor ANSI it emits into <span>s
carrying the CSS classes defined in public/index.html.

    # emit the <pre> inner HTML for a snippet
    tools/highlight_to_html.py path/to/snippet.qn
    echo 'x = #(1 2 3).collect:{ |n| n * n }' | tools/highlight_to_html.py -

    # wrap it in <pre>…</pre>, ready to drop in
    tools/highlight_to_html.py --pre snippet.qn

    # print the matching CSS palette block (keep index.html's <style> in sync)
    tools/highlight_to_html.py --css

The palette is the Quoin standard, lifted from the VM's source of truth:
    building_blocks_vm/crates/quoin-syntax/src/highlight.rs  ::  colors_for()
Locals cycle through 4 colors by scope depth (.v0–.v3); block braces cycle
through 5 by nesting depth (.b0–.b4); collection braces `#( )` are one color.

SITE DEVIATION: `qn highlight` colors the `<- -> ^> <--` arrows plain white
(they're operators). This site keeps them brand-gold (.kw) on purpose. That's
applied here by default; pass --no-gold-arrows for the pure standard.

The `qn` binary is found via $QN_BIN, then PATH, then a sibling building_blocks_vm
checkout's target/{debug,release}. Override with --qn or $QN_BIN.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

# class -> (hex, extra CSS, description). Mirrors colors_for() in the VM.
# Order is the order rules are emitted by --css.
PALETTE = [
    ("cmt",  "b9bdba", "opacity:.72",      "comment (dim · the ;lw flag)"),
    ("num",  "00bfff", "",                 "number"),
    ("str",  "4682b4", "",                 "string / symbol / regex"),
    ("ivar", "6ab1c2", "",                 "instance variable  @x"),
    ("sel",  "ab82ff", "",                 "message selector"),
    ("typ",  "ef65a5", "",                 "class / global / nil·true·false"),
    ("ns",   "d53b82", "",                 "namespace  [Mod]"),
    ("key",  "e0a45a", "font-weight:600",  "keyword  (use)"),
    ("path", "6aa9e0", "",                 "use target path"),
    ("arr",  "93c6a5", "",                 "collection brace  #( )"),
    # block braces, cycled by nesting depth
    ("b0", "f79c88", "", "brace depth%5=0"), ("b1", "80f0ff", "", "brace depth%5=1"),
    ("b2", "fa859d", "", "brace depth%5=2"), ("b3", "eabe95", "", "brace depth%5=3"),
    ("b4", "a4dbbe", "", "brace depth%5=4"),
    # locals, cycled by scope depth
    ("v0", "5fd7af", "", "local scope%4=0"), ("v1", "aeb1ab", "", "local scope%4=1"),
    ("v2", "c79ca9", "", "local scope%4=2"), ("v3", "85b9a5", "", "local scope%4=3"),
]
HEX2CLASS = {hexc: cls for cls, hexc, _x, _d in PALETTE}
WHITE = "ffffff"  # Operator / default text -> the <pre> base color, left unspanned.

# Arrow tokens this site keeps brand-gold even though the standard colors them white.
ARROW_RE = re.compile(r"<--|->|<-|\^>")
# A truecolor SGR run: ESC[38;2;R;G;B(;flag…)m  followed by text up to the next ESC.
RUN_RE = re.compile(r"\x1b\[38;2;(\d+);(\d+);(\d+)(?:;\d+)*m([^\x1b]*)")


def find_qn(explicit=None):
    for cand in (explicit, os.environ.get("QN_BIN")):
        if cand and os.path.exists(cand):
            return cand
    onpath = shutil.which("qn")
    if onpath:
        return onpath
    here = os.path.dirname(os.path.abspath(__file__))
    roots = [
        os.path.normpath(os.path.join(here, "..", "..", "building_blocks_vm")),
        os.path.expanduser("~/code/building_blocks_vm"),
    ]
    for root in roots:
        for profile in ("debug", "release"):
            cand = os.path.join(root, "target", profile, "qn")
            if os.path.exists(cand):
                return cand
    sys.exit("error: could not find the `qn` binary. Set $QN_BIN or pass --qn.")


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def emit_white(t, gold_arrows):
    if not gold_arrows:
        return esc(t)
    out, last = [], 0
    for m in ARROW_RE.finditer(t):
        out.append(esc(t[last:m.start()]))
        out.append(f'<span class="kw">{esc(m.group(0))}</span>')
        last = m.end()
    out.append(esc(t[last:]))
    return "".join(out)


def ansi_to_html(ansi, gold_arrows=True):
    out = []
    for r, g, b, text in RUN_RE.findall(ansi):
        if text == "":
            continue
        hexc = f"{int(r):02x}{int(g):02x}{int(b):02x}"
        if hexc == WHITE:
            out.append(emit_white(text, gold_arrows))
            continue
        cls = HEX2CLASS.get(hexc)
        if cls is None:
            sys.stderr.write(f"warning: unmapped color #{hexc} for {text!r}\n")
            out.append(esc(text))
        else:
            out.append(f'<span class="{cls}">{esc(text)}</span>')
    # `qn highlight` ends every visual line with a white run holding just "\n";
    # drop the final one so <pre> gains no trailing blank line.
    return "".join(out).rstrip("\n")


def highlight(source_path, qn_bin, gold_arrows=True):
    ansi = subprocess.run(
        [qn_bin, "highlight", source_path],
        capture_output=True, text=True, check=True,
    ).stdout
    return ansi_to_html(ansi, gold_arrows)


def css_block():
    lines = ["  /* Quoin standard syntax palette — generated by tools/highlight_to_html.py --css */",
             "  /* source of truth: building_blocks_vm/crates/quoin-syntax/src/highlight.rs colors_for() */"]
    for cls, hexc, extra, desc in PALETTE:
        if cls in ("b1", "v1"):  # group the cycled families onto compact lines
            continue
        if cls == "b0":
            rules = "".join(f".{c}{{color:#{h}}}" for c, h, *_ in PALETTE if c.startswith("b"))
            lines.append(f"  {rules}  /* block braces, by nesting depth */")
            continue
        if cls == "v0":
            rules = "".join(f".{c}{{color:#{h}}}" for c, h, *_ in PALETTE if c.startswith("v"))
            lines.append(f"  {rules}  /* locals, by scope depth */")
            continue
        if cls.startswith(("b", "v")):
            continue
        body = f"color:#{hexc}" + (f";{extra}" if extra else "")
        lines.append(f"  .{cls}{{{body}}}".ljust(40) + f"/* {desc} */")
    lines.append("  .kw{color:var(--accent)}".ljust(40) + "/* brand gold — <- -> ^> (site deviation) */")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Quoin snippet -> highlighted HTML for the site.")
    ap.add_argument("file", nargs="?", help="path to a .qn snippet, or - for stdin")
    ap.add_argument("--css", action="store_true", help="print the CSS palette block and exit")
    ap.add_argument("--pre", action="store_true", help="wrap output in <pre>…</pre>")
    ap.add_argument("--qn", help="path to the qn binary (else $QN_BIN / PATH / sibling checkout)")
    ap.add_argument("--no-gold-arrows", action="store_true",
                    help="color <- -> ^> as plain operators (pure standard, no brand gold)")
    args = ap.parse_args()

    if args.css:
        print(css_block())
        return
    if not args.file:
        ap.error("a .qn file (or - for stdin) is required unless --css is given")

    qn_bin = find_qn(args.qn)
    tmp = None
    try:
        if args.file == "-":
            import tempfile
            fd, tmp = tempfile.mkstemp(suffix=".qn")
            with os.fdopen(fd, "w") as f:
                f.write(sys.stdin.read())
            src = tmp
        else:
            src = args.file
        html = highlight(src, qn_bin, gold_arrows=not args.no_gold_arrows)
    finally:
        if tmp:
            os.unlink(tmp)

    sys.stdout.write(f"<pre>{html}</pre>\n" if args.pre else html + "\n")


if __name__ == "__main__":
    main()
