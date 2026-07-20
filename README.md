# skills

내가 직접 만들어 쓰는 Claude Code 개인 스킬 모음 + 마켓플레이스 플러그인 설치 가이드.

## 개인 스킬

`~/.claude/skills/` 아래에 두는 직접 만든 스킬들. 본문은 영어 우선 + 섹션별 `> 한글:` 병기(에이전트는 영어, 사람은 한글로 읽기 쉽게).

### 단일 스킬

| 스킬 | 설명 |
|------|------|
| [`browser-access`](./browser-access/SKILL.md) | 브라우저 기반 작업(UI 검증, 시각 테스트, 네트워크 디버깅, DOM 검사) 시작 시. Claude in Chrome 우선, Chrome DevTools MCP는 계측·폴백. 브라우저 MCP 실패·401/403·로그인 화면·권한 부여 필요 시에도 사용. |
| [`cashdoc-webview-worktree`](./cashdoc-webview-worktree/SKILL.md) | cashdoc-webview git 워크트리 부트스트랩 — 새 워크트리에서 node_modules/.env 셋업해 lint/typecheck/build 되게. pnpm/engine/env/TTY 에러나 커밋 전 검증 시. |
| [`running-cashdoc-simulator`](./running-cashdoc-simulator/SKILL.md) | cashdoc-webview 네이티브 앱 시뮬레이터(apps/simulator, `<branch>.sim.cashdoc.me`) 로컬 실행·디버깅 — localias 데몬/sudo/stuck-reload, 기기 없이 dev-login 토큰 주입, 웹뷰 빈 화면·프록시 502, 인앱(Bearer) 인증 검증 시. |
| [`moneple-cashdoc-local-dev`](./moneple-cashdoc-local-dev/SKILL.md) | moneple(MonepleMainWeb) cashdoc 커뮤니티 로컬 dev 서버 실행 — 배포본으로 바운스/구버전 표시될 때, 검색바·헤더 변경 검증 시. |
| [`ship-pr`](./ship-pr/SKILL.md) | 기능/수정이 배포 준비 완료됐을 때 — 브랜치·커밋 후 dev 배포 및 리뷰용 PR 생성. |
| [`test-followup`](./test-followup/SKILL.md) | 프로덕션 코드 작성/수정 후 완료 보고 전 — 변경분에 대한 테스트 추가 제안 트리거. |

### dev-pipeline (이슈→PR 오케스트레이션 세트)

`dev-pipeline`이 오케스트레이터, `dp-*`는 각 단계를 서브에이전트로 실행하는 단계 스킬. 메인이 단계마다 `Agent` 도구로 위임 → 서브는 요약만 반환(메인 컨텍스트 린). 순차 파이프라인, 파일 핸드오프, 단계별 승인 게이트.

| 스킬 | 단계 | 설명 |
|------|------|------|
| [`dev-pipeline`](./dev-pipeline/SKILL.md) | — | 오케스트레이터. 이슈→플랜→준비→구현→검토→테스트→PR/배포→아카이브 전체 조율 + 승인 게이트 관리. |
| [`dp-context`](./dp-context/SKILL.md) | 1 | 이슈(Jira/Slack) 읽고 정리 → plan.md/todo.md 산출. (opus) |
| [`dp-prepare`](./dp-prepare/SKILL.md) | 2 | repo 감지 후 워크트리/브랜치 생성, env 복사, 의존성 설치. |
| [`dp-implement`](./dp-implement/SKILL.md) | 3 | 워크트리 안에서 plan대로 구현. (복잡하면 opus) |
| [`dp-review`](./dp-review/SKILL.md) | 4 | diff 5축 코드 검토(정확성/가독성/아키텍처/보안/성능). |
| [`dp-test`](./dp-test/SKILL.md) | 5 | 테스트 실행·작성, 런타임 검증, 수용 기준 대조. |
| [`dp-ship`](./dp-ship/SKILL.md) | 6 | PR 생성 → CI 확인 → **배포 전 승인** → dev 배포. |
| [`dp-archive`](./dp-archive/SKILL.md) | 7 | 워크트리 삭제 + 작업 내역 영구 기록(나중 검색용). |

### 설치

이 레포를 클론해 개인 스킬을 `~/.claude/skills/`로 복사:

```bash
git clone https://github.com/topeanut/skills.git
# 전체 복사 (SKILL.md를 가진 디렉토리만)
cp -R skills/*/ ~/.claude/skills/
```

각 스킬은 `<스킬이름>/SKILL.md` 한 파일로 구성. 폴더째 `~/.claude/skills/` 아래 두면 Claude Code가 자동 인식.

### 동기화 규칙

개인 스킬이 **새로 생기거나 변경되면 이 레포에 반영**한다(commit & push). 정본은 `~/.claude/skills/`, 백업·공유본은 이 GitHub 레포. 자세한 규칙은 전역 `~/.claude/CLAUDE.md`에 기재.

## 마켓플레이스 플러그인 (제3자 스킬)

아래는 직접 만든 게 아니라 마켓플레이스에서 받은 플러그인 스킬들. 저작권은 각 원저자에게 있으므로 이 레포에는 포함하지 않고 설치법만 정리.

Claude Code에서 슬래시 명령으로 설치:

```
# 1) 마켓플레이스 등록
/plugin marketplace add <github-repo>

# 2) 플러그인 설치
/plugin install <plugin>@<marketplace>
```

### 사용 중인 플러그인 목록

| 플러그인 | 마켓플레이스 (GitHub) | 설치 명령 |
|----------|----------------------|-----------|
| `agent-skills` (개발 워크플로 스킬 모음: spec/plan/build/test/review/ship 등) | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | `/plugin marketplace add addyosmani/agent-skills`<br>`/plugin install agent-skills@addy-agent-skills` |
| `superpowers` (brainstorming, TDD, systematic-debugging 등) | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | `/plugin marketplace add anthropics/claude-plugins-official`<br>`/plugin install superpowers@claude-plugins-official` |
| `caveman` (초압축 커뮤니케이션 모드 + cavecrew 서브에이전트) | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | `/plugin marketplace add JuliusBrussee/caveman`<br>`/plugin install caveman@caveman` |
| `warp` | [warpdotdev/claude-code-warp](https://github.com/warpdotdev/claude-code-warp) | `/plugin marketplace add warpdotdev/claude-code-warp`<br>`/plugin install warp@claude-code-warp` |

설치 후 `/plugin` 으로 활성화 상태 확인 가능. 등록한 마켓플레이스는 `/plugin marketplace list` 로 조회.

> 참고: 플러그인은 원저자 레포에서 직접 받는 게 정석. 버전·라이선스는 각 레포 기준을 따른다.
