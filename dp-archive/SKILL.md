---
name: dp-archive
description: Use when a dev-pipeline task is shipped and you need to clean up and record what was done. Use when removing the CSD-XXXX worktree and writing a permanent searchable archive note so the work can be recalled later ("did I do this before?").
---

# dp-archive — Cleanup + Work Archive

**Step 7 (final step)** of the dev-pipeline. Removes the worktree and writes a **permanent record** of the work done. (sonnet)

> 한글: dev-pipeline의 **7단계(마지막)**. 워크트리를 정리하고 작업 내역을 **영구 기록**한다. (sonnet)

## Inputs

- Issue number, repo, branch, worktree path, `pr_url`, `plan.md`/`state.md`, list of changed files

> 한글: 이슈번호, repo, branch, worktree 경로, `pr_url`, `plan.md`/`state.md`, 변경 파일 목록

## Procedure

1. **Write cycle note** — `features/<slug>/cycles/<seq>-<type>-<ISSUE>.md` based on `templates/cycle.md`.
2. **Update feature index** — add a row to the cycle list in `features/<slug>/feature.md` and update the status.
3. **Update spec status** — reflect the "last updated" date and acceptance criteria check state in `spec.md` (bugfix: check only, no change history entry).
4. **Update global mapping** — in `features/index.md`, add a slug row (if new feature) and append this ISSUE to the issue list.
5. **Remove the worktree:**
   ```bash
   git worktree remove <worktree-path>        # 변경 남았으면 확인 후 --force
   git worktree prune
   ```
   - Before removal, confirm there are no unpushed commits or unsaved changes. If any exist, stop and report to the user.
6. **Clean up the run directory (optional).** `~/.claude/dev-pipeline/runs/<REPO>-<ISSUE>/` may be kept or removed — the authoritative record has been moved to the feature folder, so it is safe to delete.

> 한글:
> 1. **사이클 노트 작성** — `templates/cycle.md` 기반 `features/<slug>/cycles/<seq>-<type>-<ISSUE>.md`.
> 2. **기능 인덱스 갱신** — `features/<slug>/feature.md` 사이클 목록에 행 추가, 상태 갱신.
> 3. **스펙 상태 갱신** — `spec.md`의 "최종 갱신"·수용기준 체크 상태 반영(bugfix는 체크만, 변경이력 추가 없음).
> 4. **전역 매핑 갱신** — `features/index.md`에 (신규 기능이면) slug 행 추가, 이슈 목록에 이번 ISSUE 추가.
> 5. **워크트리 삭제:** 삭제 전 미푸시 커밋·미저장 변경 없는지 확인. 있으면 멈추고 유저에게 보고.
> 6. **런 디렉토리 정리(선택).** `~/.claude/dev-pipeline/runs/<REPO>-<ISSUE>/`는 보존하거나 정리 — 정본 기록은 feature 폴더로 옮겨졌으므로 안전.

## Return (to orchestrator)

- Cycle note path + updated feature.md / spec.md / index.md paths
- Worktree removal result
- Pipeline completion summary (issue, PR, deployment status)

> 한글:
> - cycle note 경로 + 갱신된 feature.md/spec.md/index.md 경로
> - 워크트리 삭제 결과
> - 파이프라인 완료 요약(이슈, PR, 배포 상태)

## Prohibited

- Do not remove a worktree that has unpushed or unsaved changes without explicit confirmation.
- Do not guess the date — always record the actual absolute date (today's real date).

> 한글:
> - 미푸시/미저장 변경이 있는 워크트리를 확인 없이 삭제 금지.
> - 날짜는 추정 금지 — 실제 오늘 날짜(절대값)로 기록.
