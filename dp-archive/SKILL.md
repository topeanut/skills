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

1. **Write permanent archive** — `~/.claude/dev-pipeline/archive/<ISSUE>-<slug>.md`:
   ```markdown
   # <ISSUE> — <한 줄 제목>
   - repo: <repo>
   - branch: <branch>
   - pr: <pr_url>
   - issue: <issue_url>
   - 완료일: <YYYY-MM-DD>   # 오늘 날짜를 절대 날짜로

   ## 무엇을 했나
   - <변경 요약 3~6줄>

   ## 바뀐 파일
   - <주요 파일 목록>

   ## 결정/메모
   - <state.md decisions 정리 — 나중에 "왜 이렇게 했지"에 답할 내용>
   ```
   - Purpose: a single searchable file so that the question "did I do something like this before?" can be answered later.
2. **Remove the worktree:**
   ```bash
   git worktree remove <worktree-path>        # 변경 남았으면 확인 후 --force
   git worktree prune
   ```
   - Before removal, confirm there are no unpushed commits or unsaved changes. If any exist, stop and report to the user.
3. **Clean up the run directory (optional).** `~/.claude/dev-pipeline/runs/<REPO>-<ISSUE>/` may be kept or removed — the authoritative record has been moved to the archive, so it is safe to delete.

> 한글:
> 1. **영구 아카이브 작성** — 목적: 나중에 "예전에 이런 작업 안 했나?" 질문에 답하도록 검색 가능한 한 파일.
> 2. **워크트리 삭제:** 삭제 전 미푸시 커밋·미저장 변경 없는지 확인. 있으면 멈추고 유저에게 보고.
> 3. **런 디렉토리 정리(선택).** `~/.claude/dev-pipeline/runs/<REPO>-<ISSUE>/`는 보존하거나 정리 — 정본 기록은 archive로 옮겨졌으므로 안전.

## Return (to orchestrator)

- Archive file path
- Worktree removal result
- Pipeline completion summary (issue, PR, deployment status)

> 한글:
> - 아카이브 파일 경로
> - 워크트리 삭제 결과
> - 파이프라인 완료 요약(이슈, PR, 배포 상태)

## Prohibited

- Do not remove a worktree that has unpushed or unsaved changes without explicit confirmation.
- Do not guess the date — always record the actual absolute date (today's real date).

> 한글:
> - 미푸시/미저장 변경이 있는 워크트리를 확인 없이 삭제 금지.
> - 날짜는 추정 금지 — 실제 오늘 날짜(절대값)로 기록.
