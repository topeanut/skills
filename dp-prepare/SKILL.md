---
name: dp-prepare
description: Use when a dev-pipeline plan is approved and you need an isolated workspace before implementing. Use when creating a feature branch and git worktree for a CSD-XXXX issue, copying env, and installing dependencies so lint/typecheck/build run.
---

# dp-prepare — Worktree / Branch Preparation

**Stage 2** of the dev-pipeline. Creates an isolated workspace. No implementation happens here. (sonnet)

> 한글: dev-pipeline의 **2단계**. 격리된 작업 공간을 만든다. 구현은 안 한다. (sonnet)

## Input

- repo, issue number (`CSD-XXXX`), short slug, run directory / `state.md` path

> 한글: repo, 이슈번호(`CSD-XXXX`), 짧은 슬러그, 런 디렉토리/`state.md` 경로

## Procedure

1. **Detect repo and branch:**
   - **cashdoc-webview** → follow the `cashdoc-webview-worktree` skill as-is (worktree add based on latest origin/main, Node 22 PATH, `CI=true pnpm install --prefer-offline`, copy `.env`/`.env.test`, typecheck/lint for changed packages).
   - **Other repos** → use the general procedure below.

2. **General procedure (non-cashdoc-webview):**
   ```bash
   git fetch origin main
   git worktree add -b feat/CSD-XXXX-<slug> ../<repo>-CSD-XXXX origin/main
   # env copy (from sibling checkout — safe because gitignored)
   cp ../<repo>/.env <new-worktree>/.env 2>/dev/null || true
   # dependencies: based on lockfile
   #   pnpm → CI=true pnpm install --prefer-offline
   #   npm  → npm ci
   #   yarn → yarn install --frozen-lockfile
   ```
   - Branch name **must include `CSD-XXXX`** (omitting it causes PR to be auto-closed).
   - **Must be based on the latest `origin/main`** (stale base is not allowed).

3. **Verification.** Confirm that typecheck/lint run on the packages to be changed (= setup succeeded). Success is judged by no new errors relative to changed files.

4. **Open in Cursor.** After the worktree is ready and verified, open it in a new Cursor window so work can start in the right branch. Applies to **both** repo paths (cashdoc-webview and general).
   ```bash
   cursor -n <new-worktree>
   ```
   - The worktree already has `feat/CSD-XXXX-<slug>` checked out, so opening the folder opens the branch.
   - Non-blocking: if `cursor` is missing or fails, report it but do not fail the stage.

5. **Switch the session into the worktree (so Claude status follows the branch).** A plain `git worktree add` is invisible to Claude Code's native worktree panel ("for agents"), so the status line keeps showing `main`. After the worktree exists, enter it with the native tool so the session cwd + status track the new branch:
   ```
   EnterWorktree(path: <new-worktree absolute path>)
   ```
   - Use **`path`** (the worktree you just created with `git worktree add`), **not `name`** — `name` would create a second, duplicate worktree under `.claude/worktrees/`.
   - **Who runs it:** the **MAIN orchestrator session**, not a delegated sub-agent. A sub-agent's cwd is pinned at launch, so `EnterWorktree` from the sub-agent only switches that agent and leaves the parent session's status on `main`. If dp-prepare ran as a sub-agent, it returns the worktree path and the orchestrator calls `EnterWorktree(path: ...)` after the sub-agent finishes.
   - `ExitWorktree` with `action: "keep"` returns to the original directory without removing the worktree (it refuses to remove a `git worktree add` worktree anyway).

> 한글:
> 1. **repo 감지 후 분기:** cashdoc-webview이면 `cashdoc-webview-worktree` 스킬을 따른다. 그 외 repo는 아래 일반 절차를 따른다.
> 2. **일반 절차:** 브랜치명에 반드시 `CSD-XXXX` 포함. 반드시 최신 `origin/main` 기반으로 생성.
> 3. **검증:** 변경 예정 패키지에서 typecheck/lint가 정상 실행되는지 확인. 변경 파일 기준 새 에러 없음으로 판단.
> 4. **Cursor에서 열기:** 워크트리 준비·검증 완료 후 `cursor -n <워크트리경로>`로 **새 창**에서 연다. **두 repo 흐름 모두** 적용(cashdoc-webview, 일반). 워크트리에 이미 `feat/CSD-XXXX-<slug>`가 체크아웃돼 있어 폴더를 열면 그 브랜치가 열린다. `cursor` 없거나 실패해도 단계 실패로 처리하지 말고 보고만 한다.
> 5. **세션을 워크트리로 진입(Claude status가 브랜치를 따라가게):** 순수 `git worktree add`는 Claude Code 네이티브 워크트리 패널("for agents")에 안 잡혀서 status가 계속 `main`으로 보인다. 워크트리 생성 후 네이티브 도구로 진입시켜 세션 cwd·status가 새 브랜치를 가리키게 한다 → `EnterWorktree(path: <워크트리 절대경로>)`. **반드시 `path` 사용**(방금 만든 워크트리), `name`은 `.claude/worktrees/`에 중복 워크트리를 새로 만드니 쓰지 말 것. **실행 주체는 메인 오케스트레이터 세션**이다 — 서브에이전트는 cwd가 launch 시 고정되어 서브에서 `EnterWorktree`해도 부모 세션 status는 `main`에 남는다. dp-prepare가 서브로 돌았다면 워크트리 경로만 반환하고, 서브 종료 후 오케스트레이터가 `EnterWorktree(path: ...)`를 호출한다. 되돌아갈 땐 `ExitWorktree(action: "keep")`(`git worktree add` 워크트리는 어차피 remove 거부됨).

## Return (to orchestrator)

- Created `branch` and `worktree` path → to be recorded in state.md
- Dependency installation / verification result (success/failure), and cause if failed

> 한글: 생성한 `branch`, `worktree` 경로를 state.md에 기록되도록 반환. 의존성 설치/검증 결과(성공/실패), 실패 시 원인도 포함.

## Restrictions

- Do not write any feature code. This stage is workspace preparation only.
- Do not commit env files (keep them gitignored).

> 한글: 기능 코드 작성 금지. 이 단계는 workspace 준비만. env 파일 커밋 금지(gitignore 유지).
