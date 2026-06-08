# skills

내가 직접 만들어 쓰는 Claude Code 개인 스킬 모음 + 마켓플레이스 플러그인 설치 가이드.

## 개인 스킬

`~/.claude/skills/` 아래에 두는 직접 만든 스킬들.

| 스킬 | 설명 |
|------|------|
| [`chrome-devtools-mcp-auth`](./chrome-devtools-mcp-auth/SKILL.md) | 브라우저 기반 작업(UI 검증, 시각 테스트, 네트워크 디버깅, DOM 검사) 시작 시. Chrome DevTools MCP 실패·401/403·로그인 화면·권한 부여 필요 시에도 사용. |
| [`ship-pr`](./ship-pr/SKILL.md) | 기능/수정이 배포 준비 완료됐을 때 — 브랜치·커밋 후 dev 배포 및 리뷰용 PR 생성. |
| [`test-followup`](./test-followup/SKILL.md) | 프로덕션 코드 작성/수정 후 완료 보고 전 — 변경분에 대한 테스트 추가 제안 트리거. |

### 설치

이 레포를 클론해 개인 스킬을 `~/.claude/skills/`로 복사:

```bash
git clone https://github.com/topeanut/skills.git
cp -R skills/chrome-devtools-mcp-auth skills/ship-pr skills/test-followup ~/.claude/skills/
```

각 스킬은 `<스킬이름>/SKILL.md` 한 파일로 구성. 폴더째 `~/.claude/skills/` 아래 두면 Claude Code가 자동 인식.

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
