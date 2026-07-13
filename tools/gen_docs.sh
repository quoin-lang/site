#!/bin/sh
# Regenerate the hosted documentation from a Quoin VM checkout:
#
#   public/book/       <- qn doc --md docs/language     (the language reference)
#   public/reference/  <- qn doc --stdlib               (the stdlib API reference)
#
# Usage: tools/gen_docs.sh [path-to-quoin-checkout]
# The checkout defaults to a sibling `quoin` directory; the qn binary is taken
# from $QN_BIN or the checkout's target/{debug,release}.
set -eu

site="$(cd "$(dirname "$0")/.." && pwd)"
vm="${1:-$site/../quoin}"
[ -d "$vm/docs/language" ] || { echo "error: no docs/language under $vm (pass the checkout path)" >&2; exit 1; }

qn="${QN_BIN:-}"
if [ -z "$qn" ]; then
    for profile in debug release; do
        [ -x "$vm/target/$profile/qn" ] && qn="$vm/target/$profile/qn" && break
    done
fi
[ -n "$qn" ] || { echo "error: no qn binary; set \$QN_BIN or build the checkout" >&2; exit 1; }

rm -rf "$site/public/book" "$site/public/reference"
# --stdlib-path: book code spans naming stdlib classes link into the sibling reference.
(cd "$vm" && QUOIN_STDLIB="$vm/qnlib" "$qn" doc --md docs/language --stdlib-path ../reference --out "$site/public/book")
(cd "$vm" && QUOIN_STDLIB="$vm/qnlib" "$qn" doc --stdlib --out "$site/public/reference")
