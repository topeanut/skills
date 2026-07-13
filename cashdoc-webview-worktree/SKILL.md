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

## 1. Node 24 (Required)

Root and `apps/web` have `engines.node` set to `24.x`, and `.nvmrc` pins `v24.15.0`. On a mismatched version `pnpm install` still completes but emits `[WARN] Unsupported engine`, and the local run drifts from CI. Use nvm to put Node 24 on PATH (repeat for every Bash call):

> 한글: 루트와 `apps/web`의 `engines.node`가 `24.x`이고 `.nvmrc`는 `v24.15.0` 고정. 버전이 어긋나면 `pnpm install`이 실패하진 않지만 `[WARN] Unsupported engine`이 뜨고 CI와 로컬이 어긋난다. nvm으로 24를 PATH에 올린다(매 Bash 호출마다).

```bash
export PATH="$HOME/.nvm/versions/node/v24.15.0/bin:$PATH"   # 설치본은 `ls ~/.nvm/versions/node`로 확인
```

> ⚠️ 이 레포는 과거 `22.x`였다가 24로 올라갔다. 엔진 요구는 **항상 `.nvmrc`와 루트 `package.json`의 `engines`로 확인**하고, 이 문서 숫자를 그대로 믿지 말 것.

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
cp ../cashdoc-webview/apps/astro/.env apps/astro/.env         # astro 작업이면 필수
```

> `apps/astro`에도 별도 `.env`가 있다. astro 페이지를 건드리면서 이걸 빠뜨리면 typecheck/build가 env 검증에서 깨진다.

`.env` is gitignored so it will not be committed — this is safe.

> 한글: `.env`는 gitignore라 커밋되지 않으니 안전.

## 4. Verification

`turbo`는 전역 PATH에 없다. **로컬 바이너리로 호출**한다:

```bash
# 변경 파일이 속한 패키지만 (astro/web/ui/utils 등)
./node_modules/.bin/turbo typecheck lint --filter=@cashdoc/astro --filter=@cashdoc/ui
```

> ⚠️ **lint는 clean main에서도 red다.** `@cashdoc/astro`는 `no-deprecated-typography` 경고만 900건대(130여 파일)가 쌓여 있고 oxlint가 exit 1로 끝난다. turbo는 이때 형제 task(typecheck)까지 같이 죽여서 `typecheck: [ELIFECYCLE] Command failed`를 찍는데 **typecheck가 실패한 게 아니다.** 헷갈리면 typecheck를 단독으로 돌려 exit code를 확인한다:
>
> ```bash
> cd apps/astro && pnpm run typecheck; echo "exit=$?"   # 정상이면 exit=0 / "0 errors"
> ```
>
> 판정 기준은 **내가 바꾼 파일이 새 에러를 만들었는가**다. 전체 lint가 red인 것 자체는 baseline이므로 착수 직후(무수정 상태) 한 번 돌려 baseline을 기록해두면 비교가 쉽다.

- lint = **oxlint** (`oxlint . --type-aware`). 특정 파일만: `cd apps/astro && ../../node_modules/.bin/oxlint <path...>`.
- 포맷 = prettier (`@ianvs/prettier-plugin-sort-imports`). 변경 파일: `./node_modules/.bin/prettier --check <path...>`, 자동수정 `--write`.
- CI 결과 해석은 `pr-ci-status` 스킬 참고 — `🔧 Quality` job이 중간 exit code를 삼키고 `보고` job만 게이트한다.

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
