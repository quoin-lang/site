# tools

## `highlight_to_html.py` — Quoin code blocks for the site

The site shows Quoin snippets in `public/index.html` `<pre>` blocks, syntax-
highlighted by hand-written `<span>`s. The colors match the language's own
highlighter so the site and the real `qn highlight` agree. Don't tint code by
hand — write the snippet as plain Quoin and run it through this tool.

```sh
# 1. write the snippet as real Quoin
cat > /tmp/snippet.qn <<'EOF'
x = #(1 2 3).collect:{ |n| n * n }
EOF

# 2. generate the <pre> inner HTML and paste it into index.html
tools/highlight_to_html.py /tmp/snippet.qn          # spans only
tools/highlight_to_html.py --pre /tmp/snippet.qn    # wrapped in <pre>…</pre>
echo 'x.foo:42' | tools/highlight_to_html.py -      # or from stdin
```

The CSS classes the spans use live in `index.html`'s `<style>`. Regenerate that
palette block (e.g. if the VM's colors change) with:

```sh
tools/highlight_to_html.py --css
```

Notes:
- Needs the `qn` binary: found via `$QN_BIN`, then `PATH`, then a sibling
  `building_blocks_vm` checkout's `target/{debug,release}`. Override with `--qn`.
- The palette is the Quoin standard, mirrored from
  `building_blocks_vm/crates/quoin-syntax/src/highlight.rs` (`colors_for`).
  Locals cycle by scope (`.v0`–`.v3`), block braces by nesting depth
  (`.b0`–`.b4`), collection braces `#( )` are one color.
- **Site deviation:** the `<- -> ^> <--` arrows are kept brand-gold (`.kw`),
  not the standard's white. Pass `--no-gold-arrows` for the pure standard.
```
