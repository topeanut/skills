---
name: moneple-cashdoc-local-dev
description: Run the moneple (MonepleMainWeb) cashdoc community local dev server so its changes are actually viewable in a browser. Use when moneple cashdoc community redirects to test.cashdoc.me, when www.local.cashdoc.mnpp.cc shows old/deployed code, when verifying moneple search-bar/header changes for the cashdoc tenant, or when `local.cashdoc.mnpp.cc/community` bounces to deployed.
---

# moneple Cashdoc Community Local Dev Setup

The **cashdoc community** (`cashdoc.me/community`) served by moneple (`MonepleMainWeb`) uses a multi-tenant + subdirectory domain structure. Running `npm run dev` and opening the URL as-is will **redirect you to the deployed server**. The setup below is required to view local builds in a browser.

> 한글: moneple(`MonepleMainWeb`)의 **cashdoc 커뮤니티**(`cashdoc.me/community`)는 멀티테넌트 + 서브디렉토리 도메인 구조라, 그냥 `npm run dev` 하고 접속하면 **배포 서버로 튕긴다**. 로컬 빌드를 브라우저에서 보려면 아래 셋업이 필요하다.

## Core Principle (Why It Doesn't Show Local Code)

| URL | Where it actually goes |
|---|---|
| `www.local.cashdoc.mnpp.cc` | **CloudFront distribution** (not in `/etc/hosts` → real DNS). The `via: cloudfront` header is proof. Not local! |
| `local.cashdoc.mnpp.cc/community` | moneple tenant domain → `handleMonepleToSubdirectoryDomainRedirection` **redirects to the service domain (cashdoc.me)** → in local env this goes to `test.cashdoc.me` (deployed) |
| `localhost:3500` directly | host=localhost → not the cashdoc tenant → **blank page** |
| **`local.test.cashdoc.me/community`** | ✅ **Local cashdoc service domain** — subdirectory redirect does not fire (already on the target domain). This is the URL that serves the local build |

> 한글: 각 URL이 실제로 가는 곳을 설명한 표.
> - `www.local.cashdoc.mnpp.cc` → CloudFront 배포 (로컬 아님)
> - `local.cashdoc.mnpp.cc/community` → moneple 테넌트 도메인 → 배포 서버로 리다이렉트
> - `localhost:3500` 직접 → cashdoc 테넌트 아님 → 빈 페이지
> - **`local.test.cashdoc.me/community`** → ✅ 로컬 빌드가 뜨는 유일한 URL

`subdirectoryConfig.ts` mapping: `'local.test.cashdoc.me': 'local.cashdoc.mnpp.cc'` — the local cashdoc service domain is `local.test.cashdoc.me`.

> 한글: `subdirectoryConfig.ts`의 매핑: `'local.test.cashdoc.me': 'local.cashdoc.mnpp.cc'` — 로컬 cashdoc 서비스 도메인 = `local.test.cashdoc.me`.

## Setup Steps

> 한글: 셋업 절차

### 0. Prerequisites
- A `.env` file is required — without it, `npm run dev`'s `gqlgen` step (GraphQL codegen, rover/apollo credentials) fails and the build breaks with stale types.
- Node 22 (`engines.node`).

> 한글:
> - `.env` 필요 — 없으면 `npm run dev`의 `gqlgen`(GraphQL codegen, rover/apollo 크레덴셜)이 실패해 빌드가 stale 타입으로 깨진다.
> - Node 22 (`engines.node`).

### 1. Start moneple on the backend port (3500)
moneple's `dev-server.js` **binds directly to port 443**, which conflicts with localias (also on 443). To use it as a backend behind localias, run plain `next dev` on a different port:

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.1/bin:$PATH"
cd /Users/ljh/Desktop/work/cashwalk-repo/MonepleMainWeb-CSD-7751
NODE_TLS_REJECT_UNAUTHORIZED=0 ./node_modules/.bin/env-cmd -f ./env/.local ./node_modules/.bin/next dev --port 3500
```
- `NODE_TLS_REJECT_UNAUTHORIZED=0` — required because SSR calls a self-signed API (originally set by dev-server.js).
- `next dev` skips the custom server but `src/middleware.ts` still runs normally.
- **Must be started stably in the background** (shell exit sends SIGHUP which kills the process → exit 144). When running as an agent use `run_in_background: true`.

> 한글: moneple `dev-server.js`는 **443 직접 바인딩**이라 localias(443)와 충돌한다. localias 뒤 백엔드로 쓰려면 plain `next dev`를 다른 포트로 실행한다.
> - `NODE_TLS_REJECT_UNAUTHORIZED=0` — SSR이 self-signed API를 호출하므로 필요(원래 dev-server.js가 설정).
> - `next dev`는 custom server를 건너뛰지만 `src/middleware.ts`는 그대로 동작.
> - **반드시 백그라운드로 안정 기동**(셸 종료 시 SIGHUP로 죽음 → exit 144). 에이전트면 `run_in_background: true`.

### 2. Configure localias to route `local.test.cashdoc.me` → 3500
Add the following to `~/Library/Application Support/localias.yaml`:
```yaml
local.test.cashdoc.me: 3500
```

> 한글: `~/Library/Application Support/localias.yaml`에 `local.test.cashdoc.me: 3500` 줄을 추가한다.

### 3. Start localias (requires sudo, port 443 must be free)
```bash
sudo localias start
```
- Registers `local.test.cashdoc.me` in `/etc/hosts` and proxies HTTPS on port 443.
- **Fails if anything else is already holding port 443** ("another instance ... listening on 443"). Clean up any stray moneple-443 process (`node dev-server`) or a previous localias instance first: find the PID with `lsof -iTCP:443 -sTCP:LISTEN` and kill it.
- localias certificates use the localias own CA. **Your own browser trusts it** (system keychain), but automated (MCP/headless) Chrome uses an isolated profile and **does not trust it** (`ERR_CERT_AUTHORITY_INVALID`).

> 한글:
> - `/etc/hosts`에 `local.test.cashdoc.me` 등록 + 443에서 https 프록시.
> - **443을 다른 게 잡고 있으면 실패**한다("another instance ... listening on 443"). moneple-443 stray(`node dev-server`)나 이전 localias를 먼저 정리: `lsof -iTCP:443 -sTCP:LISTEN`로 PID 찾아 kill.
> - localias 인증서는 localias 자체 CA. **본인 브라우저는 신뢰**(시스템 키체인), 자동화(MCP/headless) 크롬은 격리 프로필이라 **신뢰 안 함**(`ERR_CERT_AUTHORITY_INVALID`).

### 4. Open in Browser
```
https://local.test.cashdoc.me/community
```
If a certificate warning appears, click Advanced → Proceed.

> 한글: 브라우저에서 cert 경고 뜨면 Advanced → Proceed를 클릭한다.

## Troubleshooting

- **`Cannot find module './vendor-chunks/@formatjs.js'`** (or other vendor-chunk errors) → stale `.next` cache. Run `rm -rf .next` and restart from step 1.
- **Still seeing old code** → you are viewing `www.local.cashdoc.mnpp.cc` (deployed). Switch to `local.test.cashdoc.me`.
- **`/community` → 308 infinite loop / redirects to test** → you are accessing via the moneple tenant domain (`*.mnpp.cc`). Use the service domain (`local.test.cashdoc.me`) to avoid the redirect.
- **Verify with curl** (automated Chrome cannot bypass the cert):
  ```bash
  curl -skL "https://local.test.cashdoc.me/ko-KR/community" | grep -o '검색할 클래스/문구'
  ```

> 한글:
> - **`Cannot find module './vendor-chunks/@formatjs.js'`** (또는 다른 vendor-chunk) → stale `.next`. `rm -rf .next` 후 1번부터 재기동.
> - **여전히 옛 코드** → `www.local.cashdoc.mnpp.cc`(배포) 보고 있는 것. `local.test.cashdoc.me`로 바꿔라.
> - **`/community` → 308 무한 루프 / test로 리다이렉트** → moneple 테넌트 도메인(`*.mnpp.cc`)으로 접속한 것. 서비스 도메인(`local.test.cashdoc.me`)으로 접속해야 리다이렉트 안 탐.
> - **검증은 curl로** (자동화 크롬은 cert 못 뚫음).

## Reverting (switching back to Yeogiya or another local setup)
Remove the `local.test.cashdoc.me: 3500` line from `localias.yaml`, then run `sudo localias reload`. Kill the moneple 3500 process.

> 한글: localias.yaml에서 `local.test.cashdoc.me: 3500` 줄 제거 + `sudo localias reload`. moneple 3500 프로세스 kill.
