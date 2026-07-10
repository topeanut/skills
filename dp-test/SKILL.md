---
name: dp-test
description: Use when dev-pipeline code passed review and you must prove it works before opening a PR. Use when running or writing tests for a CSD-XXXX change and verifying the behavior actually does what the plan requires.
---

# dp-test — Test & Verification

**Step 5** of the dev-pipeline. Proves that a change actually works as intended. (sonnet)

> 한글: dev-pipeline의 **5단계**. 변경이 실제로 동작하는지 증명한다. (sonnet)

## Inputs

- Worktree path, changed files, `plan.md` (acceptance criteria), `state.md`

> 한글: 워크트리 경로, 변경 파일, `plan.md`(수용 기준), `state.md`

## Procedure

1. **Run existing tests.** Execute the test suite within the scope of the change to confirm no regressions.
2. **Decide if new tests are needed.** Using `test-followup` criteria, determine whether the behavior change is testable; if so, write tests following the project's conventions (Vitest/Jest/Playwright, file location, naming) — applying the `agent-skills:test` principle of writing failing tests first.
3. **Runtime verification.** For UI/flow changes where unit tests are insufficient, use the `verify` skill to launch the app and observe actual behavior (see `browser-access` for browser access).
4. **Check acceptance criteria.** Confirm that the actual results satisfy each acceptance criterion in plan.md. Follow `superpowers:verification-before-completion` — secure concrete output evidence before claiming a pass.

> 한글:
> 1. **기존 테스트 실행.** 변경 영향 범위의 테스트 스위트를 돌려 회귀 없음 확인.
> 2. **새 테스트 필요 판단.** `test-followup` 기준으로 동작이 검증 가능한 변경인지 보고, 적합하면 프로젝트 컨벤션(Vitest/Jest/Playwright, 위치, 네이밍)대로 테스트 작성 — `agent-skills:test`(실패 테스트 먼저) 원칙.
> 3. **런타임 검증.** 단위 테스트로 부족한 UI/플로우 변경은 `verify` 스킬로 앱을 띄워 실제 동작 관찰(브라우저는 `browser-access` 참고).
> 4. **수용 기준 대조.** plan.md 수용 기준을 실제 결과로 충족 확인. `superpowers:verification-before-completion` — 통과 주장 전 실제 출력 근거 확보.

## Return (to orchestrator)

- The tests/commands run and their **actual results** (pass/fail counts, key output). Report failures as-is.
- Any test files added (if applicable).
- Whether acceptance criteria are met + any unresolved issues.

> 한글:
> - 실행한 테스트/명령과 **실제 결과**(통과/실패 수, 핵심 출력). 실패는 그대로 보고.
> - 추가한 테스트 파일(있으면)
> - 수용 기준 충족 여부 + 미해결 이슈

## Prohibitions

- Do not report a pass when tests have not actually passed (no baseless success claims).
- Do not alter the semantic meaning of production code just to make tests pass — that reverts to dp-implement.

> 한글:
> - 통과 안 했는데 통과로 보고 금지(근거 없는 성공 주장 금지).
> - 테스트 통과시키려 프로덕션 코드 의미 변경 금지 — 그건 dp-implement로 되돌림.
