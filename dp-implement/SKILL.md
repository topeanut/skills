---
name: dp-implement
description: Use when a dev-pipeline plan is approved and the worktree is ready, and you must write the actual code for a CSD-XXXX task following plan.md and todo.md inside the prepared worktree.
---

# dp-implement — Implementation

**Stage 3** of the dev-pipeline. Write code according to `plan.md`/`todo.md`. (Use opus for complex tasks, sonnet by default.)

> 한글: dev-pipeline의 **3단계**. `plan.md`/`todo.md`대로 코드를 작성한다. (복잡하면 opus, 기본 sonnet)

## Inputs

- Worktree path (work **inside** it), paths to `plan.md`/`todo.md`, `state.md`
- `approval_cadence` (value obtained by the orchestrator from the user): `per-step` | `after-implement` | `after-pr`

> 한글:
> - 워크트리 경로(여기 **안에서** 작업), `plan.md`/`todo.md` 경로, `state.md`
> - `approval_cadence`(오케스트레이터가 유저에게 받아 둔 값): `per-step` | `after-implement` | `after-pr`

## Procedure

1. **Work only inside the worktree.** Do not touch other worktrees or the main checkout.
2. **Thin vertical slices.** Follow `agent-skills:incremental-implementation` principles — implement in small units per todo item and verify each slice with typecheck/lint.
3. **Write code like the existing code.** Match the naming, patterns, and comment density of adjacent code. No refactors or cleanup outside the scope (scope discipline).
4. **Respect the approval cadence:**
   - `per-step` → stop and report to the orchestrator after each todo item is done (so the user can approve).
   - `after-implement` / `after-pr` → report once after the full implementation is complete.
5. **Validate.** Pass typecheck/lint scoped to changed files (filter to changed packages only). Confirm no new errors.
6. **Stop when blocked.** If the plan conflicts with the code or is ambiguous, do not guess — return with questions.

> 한글:
> 1. **워크트리 안에서만 작업.** 다른 워크트리/메인 체크아웃 건드리지 않는다.
> 2. **얇은 수직 슬라이스로.** `agent-skills:incremental-implementation` 원칙 — todo 항목 단위로 작게 구현하고 각 슬라이스를 typecheck/lint로 확인.
> 3. **기존 코드처럼 쓴다.** 인접 코드의 네이밍·패턴·주석 밀도에 맞춘다. 범위 밖 리팩터·청소 금지(scope discipline).
> 4. **승인 주기 준수:**
>    - `per-step` → todo 항목 하나 끝낼 때마다 멈추고 오케스트레이터에 보고(유저 승인 받게).
>    - `after-implement` / `after-pr` → 전체 구현 후 1회 보고.
> 5. **검증.** 변경 파일 기준 typecheck/lint 통과(변경 패키지만 필터). 새 에러 없음 확인.
> 6. **막히면 멈춤.** 플랜과 코드가 충돌하거나 모호하면 추측하지 말고 질문거리로 반환.

## Return Values (to orchestrator)

- Completed todo items, list of changed files (brief)
- typecheck/lint results
- Non-obvious implementation decisions (to be recorded in `state.md` under `decisions`) + open questions

> 한글:
> - 완료한 todo 항목, 변경 파일 목록(짧게)
> - typecheck/lint 결과
> - 비자명한 구현 결정(state.md `decisions`에 적히도록) + 미결 질문

## Prohibited

- Commit policy follows user instructions — if not explicitly stated, leave commits/pushes to the orchestrator or a later stage.
- Do not modify out-of-scope files or make bulk formatting changes.

> 한글:
> - 커밋 정책은 유저 지시 따름 — 명시 없으면 커밋/푸시는 오케스트레이터·후속 단계에 맡긴다.
> - 범위 밖 파일 수정·대량 포맷 변경 금지.
