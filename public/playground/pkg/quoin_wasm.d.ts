/* tslint:disable */
/* eslint-disable */

/**
 * Format `source` with the canonical `qn fmt` style. Returns JSON:
 * `{"ok": string}` or `{"error": string}` (a parse error, verbatim).
 */
export function fmt(source: string): string;

/**
 * Highlight `source` as an HTML fragment of `<span class="qn-…">` runs (text
 * escaped, nothing ever dropped — unspanned stretches pass through escaped).
 * Resilient: incomplete input is predictively completed and uncompletable input
 * comes back escaped-but-unstyled, so this is safe to call on every keystroke.
 * Style the classes with [`highlight_stylesheet`].
 */
export function highlight(source: string): string;

/**
 * The `qn-*` token stylesheet, generated from the same palette table the terminal
 * and the generated docs use (light scheme by default, the terminal palette under
 * `prefers-color-scheme: dark`) — the playground's colors can't drift from `qn
 * highlight`'s.
 */
export function highlight_stylesheet(): string;

export function init(): void;

/**
 * Parse and run `source` against the embedded stdlib.
 *
 * `on_output` is called as `on_output(stream, text)` with `stream` `"out"` or
 * `"err"` for every captured chunk of program output (prints, compile
 * diagnostics), in order, while the program runs. `max_batches` caps execution
 * (in dispatch batches of `QN_BATCH` instructions each; pass `undefined` for no
 * cap) — the belt-and-suspenders alongside terminating the hosting worker.
 *
 * Returns a JSON string: `{"result": string|null, "error": string|null,
 * "exitCode": number}` — `result` is the final expression pretty-rendered,
 * exactly one of `result`/`error` is non-null unless the program called
 * `Runtime.exit:`.
 */
export function run(source: string, max_batches: number | null | undefined, on_output: Function): string;

/**
 * The VM version baked into this bundle (the workspace version).
 */
export function version(): string;

export type InitInput = RequestInfo | URL | Response | BufferSource | WebAssembly.Module;

export interface InitOutput {
    readonly memory: WebAssembly.Memory;
    readonly fmt: (a: number, b: number) => [number, number];
    readonly highlight: (a: number, b: number) => [number, number];
    readonly highlight_stylesheet: () => [number, number];
    readonly init: () => void;
    readonly run: (a: number, b: number, c: number, d: any) => [number, number];
    readonly version: () => [number, number];
    readonly __wbindgen_malloc: (a: number, b: number) => number;
    readonly __wbindgen_realloc: (a: number, b: number, c: number, d: number) => number;
    readonly __wbindgen_exn_store: (a: number) => void;
    readonly __externref_table_alloc: () => number;
    readonly __wbindgen_externrefs: WebAssembly.Table;
    readonly __wbindgen_free: (a: number, b: number, c: number) => void;
    readonly __wbindgen_start: () => void;
}

export type SyncInitInput = BufferSource | WebAssembly.Module;

/**
 * Instantiates the given `module`, which can either be bytes or
 * a precompiled `WebAssembly.Module`.
 *
 * @param {{ module: SyncInitInput }} module - Passing `SyncInitInput` directly is deprecated.
 *
 * @returns {InitOutput}
 */
export function initSync(module: { module: SyncInitInput } | SyncInitInput): InitOutput;

/**
 * If `module_or_path` is {RequestInfo} or {URL}, makes a request and
 * for everything else, calls `WebAssembly.instantiate` directly.
 *
 * @param {{ module_or_path: InitInput | Promise<InitInput> }} module_or_path - Passing `InitInput` directly is deprecated.
 *
 * @returns {Promise<InitOutput>}
 */
export default function __wbg_init (module_or_path?: { module_or_path: InitInput | Promise<InitInput> } | InitInput | Promise<InitInput>): Promise<InitOutput>;
