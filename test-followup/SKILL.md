---
name: test-followup
description: Use after writing or modifying production code, before reporting the work as complete — triggers a follow-up offer to add tests for the change. Applies to features, bugfixes, and refactors with behavioral impact.
---

# Test Followup

## Overview

After writing or modifying code, **ask the user once whether to write tests for the change.** Before asking, evaluate what kind of tests would be appropriate, and present a concrete proposal so the user can make an informed decision.

**Core principle:** Do not write tests unconditionally, nor skip them unconditionally. Offer a brief proposal and hand the decision to the user.

> 한글: 코드를 짜고/고치고 나면 **사용자에게 "이 변경에 대한 테스트를 작성할지" 한 번 묻는다.** 묻기 전에 어떤 테스트가 적합한지 스스로 판단하고, 사용자가 결정할 수 있도록 구체적인 제안을 한다.
>
> **핵심 원칙:** 무조건 테스트를 쓰지도, 무조건 건너뛰지도 않는다. 짧게 제안하고 사용자에게 결정권을 넘긴다.

## When to Use

- Immediately after modifying or adding production code, before reporting "done"
- After a new feature, bug fix, or behavior-changing refactor
- Changes where behavior is verifiable: pure functions, components, page flows, API handlers, etc.

> 한글:
> - 프로덕션 코드를 수정/추가한 직후, "완료" 보고 전
> - 새 기능 / 버그 수정 / 동작이 바뀌는 리팩터 후
> - 순수 함수, 컴포넌트, 페이지 플로우, API 핸들러 등 **동작이 검증 가능한** 변경

## When NOT to Use

- Only configuration files, documentation (`*.md`), or static content were changed
- The user already wrote tests during this session, or explicitly said "skip tests" at the start
- One-off / exploratory (spike) code that will be reverted immediately

> 한글:
> - 설정 파일, 문서(`*.md`), 정적 콘텐츠만 변경한 경우
> - 사용자가 이번 작업에서 **이미 테스트를 작성**했거나, 작업 시작 시 "테스트는 빼고" 명시한 경우
> - 변경이 즉시 되돌려질 일회성/탐색적 코드(스파이크)

## Workflow

1. **Analyze the change** — What changed? What behavior or edge cases are worth verifying?
2. **Identify project conventions** — Read existing test files to determine the tooling (Vitest/Jest/Playwright/...), location (same directory / `__tests__/`), and naming (`*.spec.ts` / `*.test.ts`). Do not introduce new conventions.
3. **Decide on test type** (see table below)
4. **Propose to the user** — In 1–3 lines, specify exactly what to test, where, and which cases
5. **Handle the response**
   - **Yes** → Write the tests as proposed, run them, confirm they pass
   - **No** → Finish without further action. Do not ask again.
   - **"Later"** → Instead of writing tests, leave a one-line follow-up TODO and finish

> 한글:
> 1. **변경 분석** — 무엇이 바뀌었나? 검증 가치가 있는 동작/엣지케이스가 무엇인가?
> 2. **프로젝트 컨벤션 파악** — 기존 테스트 파일을 살펴 도구(Vitest/Jest/Playwright/...), 위치(동일 디렉토리 / `__tests__/`), 네이밍(`*.spec.ts`/`*.test.ts`)을 확인. 새 컨벤션을 만들지 말 것.
> 3. **테스트 종류 결정** (아래 표 참고)
> 4. **사용자에게 제안** — 1~3줄 이내로, 어떤 테스트를 어디에 어떤 케이스로 쓸지 구체적으로 제시
> 5. **응답 처리**
>    - **Yes** → 제안한 대로 작성, 실행해서 통과 확인
>    - **No** → 추가 작업 없이 마무리. 다시 묻지 않는다.
>    - **"나중에"** → 작성 대신, 후속 TODO를 한 줄 메모로 남기고 마무리

## Decision Guide — Which Test?

| Nature of change | Suggestion |
|---|---|
| Pure function, utility, formatter, parser | Unit test (next to the target file) |
| Single component logic / render | Component unit test |
| Page entry → user action → URL / state change | E2E scenario |
| API handler / server logic | Unit or integration |
| Refactor preserving existing behavior | Existing tests passing may be sufficient; new tests may be unnecessary — **make this option explicit when asking** |
| Bug fix | Prioritize one regression test that reproduces the bug |

> 한글: 변경 성격에 따라 테스트 종류를 결정합니다. 순수 함수/유틸은 유닛 테스트, 컴포넌트는 컴포넌트 유닛 테스트, 페이지 플로우는 E2E 시나리오, API는 유닛 또는 통합 테스트를 제안합니다. 리팩터는 기존 테스트 통과로 충분할 수 있으며, 버그 수정은 회귀 테스트 1개를 우선합니다.

## Proposal Format (how to ask the user)

> Work on the change is complete. Shall I add tests?
>
> - **Proposal:** Add `foo.spec.ts` in the same folder for the change in `apps/web/src/shared/utils/foo.ts`
> - **Cases (3):** normal input / empty string / undefined
> - Reply "yes" to proceed, "no" to skip, or "later" to leave a follow-up TODO only

The key: always specify **what / where / which cases** — keep it short.

> 한글:
> 변경 작업이 끝났습니다. 테스트를 추가할까요?
>
> - **제안:** `apps/web/src/shared/utils/foo.ts` 변경에 대해 동일 폴더에 `foo.spec.ts` 추가
> - **케이스 (3개):** 정상 입력 / 빈 문자열 / undefined
> - 진행하시려면 "예", 건너뛰려면 "아니오", 후속 TODO만 남기려면 "나중에"
>
> 핵심: **무엇을 / 어디에 / 어떤 케이스를** 명시하고 끝낸다. 길게 쓰지 않는다.

## Common Mistakes

- ❌ Creating the test file without asking first → ignores user intent
- ❌ Asking only "Shall I add tests?" without specifics → user lacks enough information to decide
- ❌ Ignoring existing project conventions and introducing new tooling or locations → read 1–2 existing spec files and follow them
- ❌ Asking again after a "no" response → one refusal is valid until the end of that task
- ❌ For a refactor, recommending only new tests without mentioning that passing existing tests may be sufficient

> 한글:
> - ❌ 묻지도 않고 테스트 파일을 먼저 만든다 → 사용자 의도를 무시
> - ❌ "테스트 추가할까요?" 같은 모호한 질문만 던진다 → 사용자가 판단할 정보 부족
> - ❌ 프로젝트 기존 컨벤션 무시하고 새 도구/위치를 도입 → 먼저 기존 spec을 1~2개 읽고 따른다
> - ❌ "no" 응답 후에도 다음 턴에 또 묻기 → 한 번 거절은 그 작업 종료까지 유효
> - ❌ 리팩터인데 "기존 테스트가 통과하면 충분"이라는 옵션을 제시하지 않고 새 테스트만 권장

## Red Flags

If you find yourself thinking any of the following, stop and return to this skill:
- "Let's write tests all at once later" → Ask now and let the user decide
- "This is too simple to need tests" → Judging simplicity is for the user, not the model
- "I already verified it works manually, so it's fine" → Manual checks don't prevent regressions; ask the user at least once

> 한글: 이런 생각이 들면 멈추고 이 스킬로 돌아온다:
> - "테스트는 다음에 한꺼번에 짜자" → 지금 한 번 묻고 사용자가 결정하게 한다
> - "이건 너무 단순해서 테스트 불필요" → 단순함의 판단은 사용자에게 넘긴다
> - "이미 동작 확인했으니 됐다" → 수동 확인은 회귀 방지가 안 된다, 그래도 사용자에게 한 번은 묻는다
