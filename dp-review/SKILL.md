---
name: dp-review
description: Use when dev-pipeline implementation is done and the diff needs review before tests and PR. Use when reviewing a CSD-XXXX change for correctness, readability, architecture, security, and performance before shipping.
---

# dp-review — Code Review

**Step 4** of the dev-pipeline. Reviews the implementation diff. (sonnet)

> 한글: dev-pipeline의 **4단계**. 구현 diff를 검토한다. (sonnet)

## Input

- Worktree path, list of changed files, `plan.md` (for acceptance-criteria cross-check), `state.md`

> 한글: 워크트리 경로, 변경 파일 목록, `plan.md`(수용 기준 대조용), `state.md`

## Procedure

1. **Obtain the diff.** In the worktree, run `git diff origin/main...HEAD`; if there are uncommitted changes, use the working-tree diff instead.
2. **Multi-axis review.** Five axes per `agent-skills:review` — correctness / readability / architecture / security / performance. (Axes can be branched within a single step.)
   - If security concerns are significant, add a `security-review` perspective.
3. **Cross-check acceptance criteria.** Verify item by item whether the acceptance criteria in plan.md are actually satisfied.
4. **Summarize findings.** One line per finding with severity tags (blocker/should/nit). Omit praise and out-of-scope suggestions.

> 한글:
> 1. **diff 확보.** 워크트리에서 `git diff origin/main...HEAD` 또는 미커밋이면 작업트리 diff.
> 2. **다축 검토.** `agent-skills:review` 기준 5축 — 정확성 / 가독성 / 아키텍처 / 보안 / 성능. (한 단계 안에서 축별로 갈래 가능)
>    - 보안 우려가 크면 `security-review` 관점 추가.
> 3. **수용 기준 대조.** plan.md의 수용 기준을 실제로 만족하는지 항목별 확인.
> 4. **소견 정리.** 심각도 태그(blocker/should/nit)로 한 줄씩. 칭찬·범위 밖 제안은 생략.

## Return (to orchestrator)

- List of findings categorized as blocker / should / nit (`path:line` + problem + fix)
- Whether acceptance criteria are satisfied
- **If there are blockers**: explicitly flag that the orchestrator should decide whether to roll back to implementation (dp-implement)

> 한글:
> - blocker / should / nit 분류된 소견 목록(`path:line` + 문제 + 수정안)
> - 수용 기준 충족 여부
> - **blocker 있으면**: 구현(dp-implement)으로 되돌릴지 오케스트레이터가 판단하도록 명시

## Prohibited

- Do not modify code (review only). Fixes are handled by re-invoking dp-implement.
- Do not argue style preferences or expand scope.

> 한글:
> - 코드 수정 금지(검토만). 수정은 dp-implement 재호출로.
> - 스타일 취향 논쟁·범위 확대 금지.
