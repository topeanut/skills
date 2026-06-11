---
name: dp-ship
description: Use when a dev-pipeline change passed tests and is ready to open a PR and deploy to dev. Use when creating the PR for a CSD-XXXX branch, checking git CI, and deploying to the dev/test branch — with a mandatory approval gate before the deploy.
---

# dp-ship — PR Creation + Dev Server Deployment

Step **6** of the dev-pipeline. Uses `ship-pr` skill commands as building blocks but **the order is different**: create the PR **first**, verify CI, **get approval before deploying**, then deploy. (sonnet)

> 한글: dev-pipeline의 **6단계**. `ship-pr` 스킬의 명령을 부품으로 쓰되 **순서가 다르다**: PR을 **먼저** 만들고, CI 확인 후, **배포 전 승인을 받고** 배포한다. (sonnet)

> ⚠️ `ship-pr` deploys first then creates the PR, but this pipeline follows **PR→CI→approval→deploy** order. Always follow this order.

> 한글: ⚠️ `ship-pr`는 배포→PR 순서지만, 이 파이프라인은 **PR→CI→승인→배포**다. 이 순서를 따른다.

## Inputs

- Worktree, branch (`feat/CSD-XXXX-...`), issue/PR information, `plan.md` (for change summary), `state.md`

> 한글: 워크트리, branch(`feat/CSD-XXXX-...`), 이슈/PR 정보, `plan.md`(변경 요약용), `state.md`

## Procedure

1. **Commit & push.** Commit any uncommitted changes, then `git push -u origin feat/CSD-XXXX-...`. **`CSD-XXXX` is mandatory** in the branch name (PR will be auto-closed without it).
2. **PR draft → user review.** Compose a PR draft using the `ship-pr` PR draft template (title: `[CSD-XXXX] feat: ...`, base: `main`, body: preceding PRs / change points / reference links / notes) and **get user approval via the orchestrator**. `gh pr create` is forbidden before approval.
3. **Create PR.** After approval, run `gh pr create --base main ...`. (If `gh` is not authenticated, ask the user to run `gh auth login`.)
4. **Verify CI.** Check the PR's git CI status (`gh pr checks <num>`, etc.). **If it fails, stop** and return an error log summary + **fix suggestions** (no automatic fixes — wait for user decision).
5. **🔴 Hard gate before deployment.** After CI passes, **user approval is mandatory** immediately before deploying to dev (the gate is held by the orchestrator). Deployment without approval is forbidden.
6. **Deploy to dev.** After approval, follow `ship-pr` deployment procedure to merge feature branch into the deploy branch:
   - cashdoc-webview → `test` branch (if `test` is checked out in another worktree, use the detached merge from `cashdoc-webview-worktree`)
   - all others → `develop`

> 한글:
> 1. **커밋 & 푸시.** 미커밋 변경 커밋 후 `git push -u origin feat/CSD-XXXX-...`. 브랜치명에 **`CSD-XXXX` 필수**(없으면 PR 자동 close).
> 2. **PR 초안 → 유저 검수.** `ship-pr`의 PR 초안 템플릿(제목 `[CSD-XXXX] feat: ...`, base `main`, 본문: 선행PR/변경점/참고링크/추가사항)으로 작성해 **오케스트레이터를 통해 유저 승인**받는다. 승인 전 `gh pr create` 금지.
> 3. **PR 생성.** 승인 후 `gh pr create --base main ...`. (`gh` 미인증이면 유저에게 `gh auth login` 요청)
> 4. **CI 확인.** PR의 git CI 상태 확인(`gh pr checks <num>` 등). **실패면 멈추고** 에러 로그 요약 + **수정 제안**을 반환(자동 수정 금지, 유저 결정 대기).
> 5. **🔴 배포 전 하드 게이트.** CI 통과 후, dev 배포 **직전 반드시 유저 승인**을 받는다(오케스트레이터가 게이트 보유). 승인 없이 배포 금지.
> 6. **dev 배포.** 승인 후 `ship-pr`의 배포 절차로 feature → 배포 브랜치 merge: cashdoc-webview → `test` 브랜치 (다른 워크트리에 `test` 체크아웃 시 `cashdoc-webview-worktree`의 detached 머지 사용) / 그 외 → `develop`

## Return Values (to Orchestrator)

- `pr_url` (recorded in state.md), CI status (passed / failed + reason)
- Deployment result (merged branch, whether push succeeded)
- Time the gate was passed and whether approval was given must be stated explicitly

> 한글:
> - `pr_url`(state.md 기록), CI 상태(통과/실패+원인)
> - 배포 결과(머지된 브랜치, push 성공 여부)
> - 게이트 통과 시점/승인 여부 명시

## Prohibitions

- **Skipping pre-deployment approval is absolutely forbidden.**
- Deploying while ignoring CI failures is forbidden.
- PR base is fixed to `main` (CLAUDE.md rule).

> 한글:
> - **배포 전 승인 생략 절대 금지.**
> - CI 실패를 무시하고 배포 금지.
> - PR base는 `main` 고정(CLAUDE.md 규칙).
