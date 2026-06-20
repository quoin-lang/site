# Deploying the Quoin site

The site is a single static page (`public/index.html`) with no build step. It's
hosted on **Cloudflare Workers (static assets)**, connected to this GitHub repo
(`quoin-lang/site`) via Workers Builds — **no GitHub Actions workflow is
involved**.

> Note: this used to target Cloudflare *Pages*, but Cloudflare now steers new
> static sites onto Workers with static assets (Pages is in maintenance mode).
> The key difference: there's no "build output directory" dashboard field — the
> assets directory is set in `wrangler.jsonc` instead.

## How a deploy happens

Push to `main` → Workers Builds deploys automatically. There is nothing to run
by hand.

## Configuration: `wrangler.jsonc`

```jsonc
{
  "name": "quoin-site",
  "compatibility_date": "2026-06-01",
  "assets": { "directory": "./public" }
}
```

- No `main` / no Worker script — `assets` alone makes it a pure static deploy.
- `assets.directory` is the equivalent of the old Pages "build output directory".
- `name` is the Worker's name; keep it in sync with the dashboard project.

## Connecting the repo (one time)

**Workers & Pages → Create → Workers → Connect to Git** → pick `quoin-lang/site`.
Workers Builds detects `wrangler.jsonc`, so:

- Build command: **(empty)**
- Deploy command: **`npx wrangler deploy`** (usually pre-filled)

## Custom domain

In the Worker: **Settings → Domains & Routes → Add → Custom Domain** →
`quoinlang.dev`. Because the DNS zone is already on Cloudflare, the record and
TLS cert are wired automatically. `quoinlang.dev` is the canonical domain;
redirect `.org`/`.com` to it with zone-level Redirect Rules.

## Local preview / manual deploy

```
npx wrangler dev      # serve ./public locally
npx wrangler deploy   # deploy by hand (Git push does this automatically)
```

## Security headers

`public/_headers` sets HSTS, CSP, `X-Content-Type-Options`, `X-Frame-Options`,
`Referrer-Policy`, `Permissions-Policy`, and COOP for every response. Workers
static assets honors this file (same format Pages used); it is not served
publicly.

The CSP is locked to `default-src 'none'` and only opens what this page actually
uses. **`style-src` includes `'unsafe-inline'`** because the page has a single
inline `<style>` block — if that's ever replaced with an external stylesheet or
hashed, tighten this. Any new resource type (a script, a web font, an external
image, an analytics call) must be added to the matching CSP directive or the
browser will block it.
