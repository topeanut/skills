---
name: dp-context
description: Use when starting a dev-pipeline task and you need to turn a Jira/issue ticket into a concrete plan. Use when given a CSD-XXXX issue, a Jira URL, pasted ticket text, or a Slack thread, and you must produce plan.md and todo.md before any code is written.
---

# dp-context — Context Collection + Planning

**Step 1** of the dev-pipeline. Read and digest the issue, then produce `plan.md` and `todo.md`. No code is touched. (Typically run with **opus**.)

> 한글: dev-pipeline의 **1단계**. 이슈를 읽어 정리하고 `plan.md`와 `todo.md`를 산출한다. 코드는 건드리지 않는다. (보통 **opus**로 실행)

## Inputs

Whatever the orchestrator provides, among the following:
- Issue number (`CSD-XXXX`), Jira URL, or **pasted issue body text**
- Related Slack channel/thread (if available)
- Run-directory path (where `state.md` and output artifacts are saved)

> Jira MCP is not currently connected. If only a URL is given with no body text, **ask the user to paste the issue body** (authentication pages cannot be read automatically).

> 한글: 오케스트레이터가 넘긴 것 중 가용한 것:
> - 이슈번호(`CSD-XXXX`), Jira URL 또는 **붙여넣은 이슈 본문 텍스트**
> - 관련 Slack 채널/스레드(있으면)
> - 런 디렉토리 경로(`state.md`, 산출물 저장 위치)
>
> Jira MCP는 현재 미연결. URL만 있고 본문이 없으면 **유저에게 이슈 본문을 붙여달라고 요청**한다(인증 페이지는 자동으로 못 읽음).

## Procedure

1. **Read the issue.** Extract the goal, acceptance criteria, constraints, and related files/screens from the body. If anything is ambiguous, state your assumptions explicitly and collect questions to ask.
2. **Augment with Slack (if available).** Use `slack_search_messages`/`slack_get_thread_replies` to gather decisions, background context, and related PRs. (Skip if unavailable.)
3. **Recon the codebase (read-only).** Use Grep/Glob to locate the areas the issue points to. Understand existing patterns and adjacent code.
4. **Write `plan.md`.** Follow the pattern from `superpowers:writing-plans` / `agent-skills:plan`. Include:
   - One-line goal, acceptance criteria (as checkable items)
   - Affected files/modules, approach, risks, and open questions
5. **Write `todo.md`.** Break work down into small, verifiable units ordered by dependency.
6. **If there are open questions,** collect them at the top of plan.md (the orchestrator will surface them during user review).

> 한글:
> 1. **이슈 읽기.** 본문에서 목표·수용기준·제약·관련 파일/화면을 추출. 모호하면 가정을 명시하고 질문거리를 모은다.
> 2. **Slack 보강(있으면).** `slack_search_messages`/`slack_get_thread_replies`로 결정·배경·관련 PR을 수집. (없으면 스킵)
> 3. **코드베이스 정찰(읽기 전용).** 이슈가 가리키는 영역을 Grep/Glob로 위치 확인. 기존 패턴·인접 코드 파악.
> 4. **`plan.md` 작성.** 패턴은 `superpowers:writing-plans` / `agent-skills:plan` 참조. 포함:
>    - 목표 한 줄, 수용 기준(체크 가능하게)
>    - 영향 파일/모듈, 접근 방식, 위험·미결 질문
> 5. **`todo.md` 작성.** 작고 검증 가능한 작업 단위로 분해, 의존 순서대로.
> 6. **미결 질문이 있으면** plan.md 상단에 모아 둔다(오케스트레이터가 유저 검토 때 함께 보여줌).

## Outputs

- `<run-directory>/plan.md`
- `<run-directory>/todo.md`

> 한글:
> - `<런디렉토리>/plan.md`
> - `<런디렉토리>/todo.md`

## Return Value (to the orchestrator)

- Issue number, repo (inferred), one-line goal
- Paths to plan.md / todo.md
- **List of open questions that must be asked of the user** (if any)

> 한글:
> - 이슈번호, repo(추정), 한 줄 목표
> - plan.md/todo.md 경로
> - **유저에게 물어야 할 미결 질문 목록**(있으면)

## Prohibitions

- Do not modify code or configuration (this step is read and document only).
- Do not create branches or worktrees (that is dp-prepare's job).

> 한글:
> - 코드/설정 수정 금지(이 단계는 읽기·문서화만).
> - 브랜치·워크트리 생성 금지(그건 dp-prepare).
