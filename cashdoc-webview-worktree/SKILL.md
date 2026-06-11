---
name: cashdoc-webview-worktree
description: Bootstrap a fresh cashdoc-webview git worktree so lint/typecheck/build run, and verify changes before commit. Use when starting work in a new cashdoc-webview worktree, when pnpm install / typecheck / lint fails on engine, env, or TTY errors, or before committing GA/review changes in this repo.
---

# cashdoc-webview Worktree Bootstrap

cashdoc-webview runs tasks in parallel using git worktrees. A new worktree created with `git worktree add` checks out **source only** — `node_modules` and `.env` are absent, so lint/typecheck/build will not work as-is. Follow the steps below to set it up.

> 한글: cashdoc-webview는 git worktree로 task를 병렬 운영한다. `git worktree add`로 만든 새 워크트리는 **소스만** 체크아웃되고 `node_modules`·`.env`가 없어 그대로는 lint/typecheck/build가 안 된다. 아래 순서로 셋업한다.

## 0. Prerequisite: Confirm You Are Based on the Latest main

Feature branches **must** be created from the latest `origin/main`.

> 한글: feature 브랜치는 **반드시 최신 `origin/main` 기반**으로 만든다.

```bash
git fetch origin main
git worktree add -b feat/CSD-XXXX-<desc> ../cashdoc-webview-CSD-XXXX origin/main
```

> ⚠️ Do not branch off a stale main. main may have received large refactors such as GA or astro migrations (e.g., GA moved from `apps/web/.../google-analytics/` → `packages/utils/src/ga/`, `logEvent` signature changed from `(appData, fn)` → `(fn)` single argument). Working from an outdated base will cause structural conflicts when merging into the test deployment branch. Before starting, run `git log origin/main -1` to confirm you are on the latest.

> 한글: stale한 main에서 분기하면 안 된다. main이 GA/astro 등 대형 리팩터를 받았을 수 있고(예: GA가 `apps/web/.../google-analytics/` → `packages/utils/src/ga/`로 이전, `logEvent`가 `(appData, fn)` → `(fn)` 단일 인자로 변경), 구식 base로 작업하면 test 배포 머지에서 구조 충돌이 난다. 작업 전 `git log origin/main -1`로 최신인지 확인.

## 1. Node 22 (Required)

`apps/web` has `engines.node` set to `22.x`. If the system default is v24 or another version, `pnpm install` will fail with `ERR_PNPM_UNSUPPORTED_ENGINE`. Use nvm to put Node 22 on PATH (repeat for every Bash call):

> 한글: `apps/web`의 `engines.node`가 `22.x`. 시스템 기본이 v24 등이면 `pnpm install`이 `ERR_PNPM_UNSUPPORTED_ENGINE`로 실패. nvm으로 22를 PATH에 올린다(매 Bash 호출마다).

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.1/bin:$PATH"   # 설치본은 `ls ~/.nvm/versions/node`로 확인
```

## 2. Install Dependencies

```bash
CI=true pnpm install --prefer-offline
```

- Without `CI=true`, purging the modules directory in non-interactive mode is blocked: `ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY`.
- Takes ~15s when the pnpm store is warm.

> 한글:
> - `CI=true` 없으면 비대화형에서 modules 디렉토리 purge가 막힌다: `ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY`.
> - pnpm store가 따뜻하면 ~15s.

## 3. Copy `.env`

A new worktree has no `.env`, so the `typegen` pre-step in typecheck fails on env schema validation (e.g., `NEXT_PUBLIC_HOSPITAL_API_URL` invalid). Copy from a sibling checkout:

> 한글: 새 워크트리엔 `.env`가 없어 typecheck의 `typegen` 선행 단계가 env 스키마 검증에서 실패한다(`NEXT_PUBLIC_HOSPITAL_API_URL` invalid 등). sibling 체크아웃에서 복사한다.

```bash
cp ../cashdoc-webview/apps/web/.env apps/web/.env
cp ../cashdoc-webview/apps/web/.env.test apps/web/.env.test   # 있으면
```

`.env` is gitignored so it will not be committed — this is safe.

> 한글: `.env`는 gitignore라 커밋되지 않으니 안전.

## 4. Verification

```bash
# 변경 파일이 속한 패키지만 (web/utils 등)
turbo typecheck lint --filter=@cashdoc/web --filter=@cashdoc/utils
```

- lint = **oxlint** (`oxlint . --type-aware`). For specific files only: `cd apps/web && ../../node_modules/.bin/oxlint <path...>`.
- format = prettier (`@ianvs/prettier-plugin-sort-imports`). Check changed files: `./node_modules/.bin/prettier --check <path...>`, auto-fix with `--write`.
- The repo may have pre-existing lint warnings/errors — judge by whether **the changed files introduce new errors**.

> 한글:
> - lint = **oxlint** (`oxlint . --type-aware`). 특정 파일만: `cd apps/web && ../../node_modules/.bin/oxlint <path...>`.
> - 포맷 = prettier (`@ianvs/prettier-plugin-sort-imports`). 변경 파일: `./node_modules/.bin/prettier --check <path...>`, 자동수정 `--write`.
> - repo 전체엔 기존 lint 경고/에러가 있을 수 있으니 **변경 파일에 새 에러가 없는지**로 판단.

## 5. Deploy / PR

Dev deployment (merging feature → `test` branch) and PR creation follow the **`ship-pr` skill**. However:

- If another worktree already has `test` checked out, a regular checkout is not possible. **Use a detached worktree for the merge**:
  ```bash
  git fetch origin test
  git worktree add --detach /tmp/deploy origin/test
  cd /tmp/deploy && git merge --no-ff feat/CSD-XXXX-... -m "Merge branch 'feat/CSD-XXXX-...' into test"
  # 충돌 해결은 regex 일괄치환 금지(파일 손상 위험) — 충돌 블록만 정확히 Edit
  git push origin HEAD:test
  cd - && git worktree remove /tmp/deploy --force
  ```
- Import order conflicts between main and test may occur due to differences in the prettier import-sort plugin. Adopt the new path (`@cashdoc/utils/*`) and remove duplicate imports.

> 한글:
> - 배포 머지는 다른 워크트리에 `test`가 체크아웃돼 있으면 일반 checkout 불가. **detached 워크트리로 머지**한다.
> - main↔test가 prettier import-sort 플러그인 차이로 import 줄에서 충돌날 수 있음. 신규 경로(`@cashdoc/utils/*`) 쪽을 채택하고 중복 import 제거.
