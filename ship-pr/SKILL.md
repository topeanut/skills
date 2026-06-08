---
name: ship-pr
description: Use when a feature or fix is ready to ship — branch created, code committed, and it's time to deploy to dev and open a PR for review.
---

# ship-pr

브랜치 생성 → 개발서버 배포 → PR 초안 검수 → PR 생성 워크플로우.

## 워크플로우

```
1. 브랜치 생성
2. 커밋 (이미 완료된 경우 스킵)
3. 개발서버 배포
4. PR 초안 작성 → 사용자 검수
5. 승인 후 PR 생성
```

## 1. 브랜치 생성

컨벤션: `feat/CSD-XXXX-<짧은-설명>` (단어 구분은 `-`)

```bash
git checkout -b feat/CSD-XXXX-short-description
git push -u origin feat/CSD-XXXX-short-description
```

## 2. 개발서버 배포

레포별 배포 대상:

| 레포 | 배포 브랜치 |
|------|------------|
| cashdoc-webview | `test` |
| 그 외 | `develop` |

```bash
# cashdoc-webview 기준
git fetch origin test
git checkout test && git pull origin test
git merge feat/CSD-XXXX-... --no-ff -m "Merge branch 'feat/CSD-XXXX-...' into test"
git push origin test
git checkout feat/CSD-XXXX-...  # 작업 브랜치로 복귀
```

## 3. PR 초안 — 반드시 사용자 검수 받기

PR 생성 전, 아래 내용을 사용자에게 보여주고 승인받아야 한다.

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

**사용자가 수정 요청하면 반영 후 재확인. 승인 후에만 `gh pr create` 실행.**

## 4. PR 생성

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

## 주의

- PR base는 `main` (CLAUDE.md 규칙)
- 브랜치명에 `CSD-` 없으면 자동 close됨
- `gh` 미인증 시 먼저 `gh auth login` 실행
