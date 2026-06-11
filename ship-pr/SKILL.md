---
name: ship-pr
description: Use when a feature or fix is ready to ship — branch created, code committed, and it's time to deploy to dev and open a PR for review.
---

# ship-pr

Branch creation → dev server deployment → PR draft review → PR creation workflow.

> 한글: 브랜치 생성 → 개발서버 배포 → PR 초안 검수 → PR 생성 워크플로우.

## Workflow

```
1. Create branch
2. Commit (skip if already done)
3. Deploy to dev server
4. Write PR draft → user review
5. Create PR after approval
```

> 한글:
> 1. 브랜치 생성
> 2. 커밋 (이미 완료된 경우 스킵)
> 3. 개발서버 배포
> 4. PR 초안 작성 → 사용자 검수
> 5. 승인 후 PR 생성

## 1. Create Branch

Convention: `feat/CSD-XXXX-<short-description>` (use `-` to separate words)

```bash
git checkout -b feat/CSD-XXXX-short-description
git push -u origin feat/CSD-XXXX-short-description
```

> 한글: 컨벤션: `feat/CSD-XXXX-<짧은-설명>` (단어 구분은 `-`)

## 2. Deploy to Dev Server

Deploy target by repository:

| Repository | Deploy Branch |
|------------|---------------|
| cashdoc-webview | `test` |
| Others | `develop` |

> 한글: 레포별 배포 대상 — cashdoc-webview는 `test` 브랜치, 그 외 레포는 `develop` 브랜치에 배포한다.

```bash
# cashdoc-webview example
git fetch origin test
git checkout test && git pull origin test
git merge feat/CSD-XXXX-... --no-ff -m "Merge branch 'feat/CSD-XXXX-...' into test"
git push origin test
git checkout feat/CSD-XXXX-...  # return to working branch
```

> 한글: cashdoc-webview 기준 예시. 머지 후 작업 브랜치로 복귀한다.

## 3. PR Draft — User Review Required

Before creating the PR, show the following draft to the user and obtain approval.

> 한글: PR 생성 전, 아래 내용을 사용자에게 보여주고 승인받아야 한다.

```
제목: [CSD-XXXX] feat: <변경 요약>
Base: main

본문:
## 선행 PR
없음 (또는 관련 PR 번호)

## 변경점
- <변경 내용>

## 참고 링크
- Jira: https://smartdoctor.atlassian.net/browse/CSD-XXXX

## 추가 사항
없음
```

**If the user requests changes, apply them and re-confirm. Only run `gh pr create` after approval.**

> 한글: 사용자가 수정 요청하면 반영 후 재확인. 승인 후에만 `gh pr create` 실행.

## 4. Create PR

```bash
gh pr create \
  --title "[CSD-XXXX] feat: <제목>" \
  --base main \
  --body "$(cat <<'EOF'
## 선행 PR
없음

## 변경점
- <내용>

## 참고 링크
- Jira: https://smartdoctor.atlassian.net/browse/CSD-XXXX

## 추가 사항
없음
EOF
)"
```

> 한글: 위 명령으로 PR을 생성한다. `--base main`과 `--title` 형식을 반드시 지킨다.

## Cautions

- PR base must be `main` (CLAUDE.md rule)
- Branch names without `CSD-` will be auto-closed
- If `gh` is not authenticated, run `gh auth login` first

> 한글:
> - PR base는 `main` (CLAUDE.md 규칙)
> - 브랜치명에 `CSD-` 없으면 자동 close됨
> - `gh` 미인증 시 먼저 `gh auth login` 실행
