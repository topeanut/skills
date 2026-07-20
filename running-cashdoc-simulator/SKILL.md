---
name: running-cashdoc-simulator
description: Use when starting or debugging the cashdoc-webview native app simulator (apps/simulator, <branch>.sim.cashdoc.me) locally — spinning it up, localias daemon/sudo/stuck-reload failures, dev-login token injection without a real device, webview blank screen or proxy 502, or verifying in-app (Bearer) auth against the hospital/cashdoc API.
---

# Running the cashdoc-webview simulator

The simulator (`apps/simulator`, `@cashdoc/simulator`) renders the cashdoc/cashwalk **native app webview in a browser** — native header, tab bar, bridges, deep links, CloudFront-style routing — with no device/app build. It is a **local dev tool on `wip/simulator`**, not merged to `main`. Full docs: `docs/SIMULATOR.md` on that branch.

## Startup order (must be in this order)

1. **Integration worktree** — simulator lives on `wip/simulator`, your work on your branch. Combine them in a throwaway worktree (never PR this to `main`):
   ```bash
   git worktree add <repo>-sim -b <yourbranch>--sim origin/wip/simulator
   git -C <repo>-sim merge <yourbranch>          # conflicts: usually infra files only
   ```
   Common conflict: `packages/infra/stacks/cloudfront-stack.ts` → keep the simulator side (`git checkout --ours`, it has the newer edge behaviors), then commit.
2. `cd <repo>-sim && pnpm install`
3. **Upstream dev servers** (proxy forwards to these — they MUST be up): `pnpm dev` (root). Serves `<branch>.next.cashdoc.me` + `<branch>.astro.cashdoc.me`.
4. **Simulator**: `pnpm --filter @cashdoc/simulator dev`. Console prints `🚀 시뮬레이터: https://<branch>.sim.cashdoc.me`.
5. Open that URL in **Chrome**. `localias list | grep '\.sim\.'` if you lost it.

## localias is the #1 time sink — check it first

Both `pnpm dev` and the simulator run `localias reload`/`start`, which write `/etc/hosts` → **need sudo the human must type**. You (the agent) cannot sudo. Symptoms & fixes:

| Symptom | Cause | Fix |
|---|---|---|
| `localias reload` fails, `sudo: a terminal is required` | daemon writing hosts needs sudo | ask human: `! sudo localias reload` |
| `daemon: Resource temporarily unavailable` / daemon won't start | a **root-owned** stuck `localias reload` holds the lock (you started it earlier via sudo) | `pgrep -fl "localias reload"` → ask human `! sudo kill -9 <pid>`, then rm `daemon.pid` + `caddy/locks/storage_clean.lock` under `~/Library/Application Support/localias/`, then `localias start` |
| aliases registered but page won't resolve | hosts file not yet written | one `! sudo localias reload` writes all pending aliases |

**Key insight:** running the sim/dev command **still registers the aliases** even when the reload step errors. So: run it once (aliases land), then have the human do ONE `sudo localias reload` (or `localias start` if the daemon is dead), then re-run without sudo — the daemon is up and no further sudo is needed. Verify: `localias status` → `daemon running with pid N` and `lsof -i :443 | grep LISTEN`.

## Login (dev-login, no real device, no credentials)

The webview needs a real dev/test token — a dummy token → SSR 500. The settings panel only has a **paste-token** field and a Kakao popup (needs a password — you can't). Use the built-in **dev-login** instead (fixed dummy account `simulator-dev`, test server skips Kakao verification — no password/credential entry):

```bash
# get a real cashdoc token, no device:
curl -sk -X POST "https://<branch>.sim.cashdoc.me/__wv/login" \
  -H 'Content-Type: application/json' -d '{"devLogin":true,"device":"iOS"}'
# → {"result":{"token":"eyJ...217 chars..."}}
```

Inject into the UI: settings (⚙, top-right "캐시닥 - 비로그인") → the "캐시닥 액세스 토큰" input is a **React controlled input**, so a plain `.value =` won't register — use the native setter:
```js
const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
set.call(input, token); input.dispatchEvent(new Event('input',{bubbles:true}));
```
Then click **적용**. Success = top-right turns green "캐시닥 - 로그인" and the phone header shows a balance pill.

## Gotchas

- **Driving the webview to a specific URL:** setting `iframe.contentWindow.location` is **silently ignored** — the simulator owns the iframe (stack stays on the old route). Navigate via the real path instead: tap the tab bar / event → consultation, or the "웹뷰 푸시 (openweb=)" button (edit its hardcoded URL in `App.tsx` if you need a fixed target).
- **Blank webview + proxy 502** (`<branch>.local.cashdoc.me` returns 502): the proxy can't reach its upstream — the root `pnpm dev` (astro/next) isn't up or ports don't match. Check `/__wv/logs` (CloudFront log viewer link in the inspector). Don't rabbit-hole on infra.
- **Verifying in-app auth without a working render:** you don't need the phone to render. The dev-login token IS the app's Bearer. Hit the API directly with **pure Bearer, no cookie** (server-side curl = no CORS, no cookie bleed) to prove the token verifies as the real account:
  ```bash
  curl -sk "https://test.api.hospitalevent.cashdoc.me/api/user/ex/myPage" \
    -H "Authorization: Bearer $TOKEN"   # real account → returns that user's history; anonymous(userKey=1) → not
  ```

## Cleanup

Background dev/sim processes and the `<repo>-sim` worktree are local-only. Remove the worktree with `git worktree remove --force <repo>-sim` and delete the `--sim` branch. Never commit the integration merge back to `main`.
