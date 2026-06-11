---
name: chrome-devtools-mcp-auth
description: Use when starting any browser-based task — UI verification, visual testing, network debugging, dev server inspection, or live DOM inspection. Also use when Chrome DevTools MCP fails, returns 401/403, shows a login page, or when MCP permissions need to be granted.
---

# Chrome DevTools MCP with Authentication

## Overview

Chrome DevTools MCP gives Claude a live browser window. Use it proactively for any browser-related task, not just when errors occur.

**Core principle:** Authentication state lives in the browser. The user performs login; Claude only verifies the result.

> 한글: Chrome DevTools MCP는 Claude에게 실시간 브라우저 창을 제공합니다. 오류가 발생했을 때뿐만 아니라, 브라우저 관련 작업이라면 적극적으로 활용하세요.
>
> **핵심 원칙:** 인증 상태는 브라우저에 존재합니다. 로그인은 사용자가 직접 수행하고, Claude는 결과만 확인합니다.

## Auto-Connection Check (Always Do First)

Before any browser task, verify the MCP is connected and Chrome is ready:

1. Call `mcp__chrome-devtools__screenshot` (or any available `mcp__chrome-devtools__*` tool)
2. If it succeeds → proceed with the task
3. If it fails → follow the setup steps below

**Chrome must be running with remote debugging enabled:**
```bash
# Mac
open -a "Google Chrome" --args --remote-debugging-port=9222

# Or if Chrome is already open, restart with:
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

After launching, retry the MCP tool call.

> 한글: 브라우저 작업을 시작하기 전에 MCP가 연결되어 있고 Chrome이 준비되었는지 확인하세요:
>
> 1. `mcp__chrome-devtools__screenshot` (또는 사용 가능한 `mcp__chrome-devtools__*` 도구) 호출
> 2. 성공하면 → 작업 진행
> 3. 실패하면 → 아래 설정 단계를 따르세요
>
> **Chrome은 원격 디버깅이 활성화된 상태로 실행 중이어야 합니다.**
>
> 실행 후 MCP 도구 호출을 다시 시도하세요.

## MCP Tool Reference

Common tools available via `mcp__chrome-devtools__*`:
- `screenshot` — capture current page
- `evaluate` — run JS in page context
- `get_console_logs` — fetch console output
- `get_network_requests` — inspect network traffic
- `navigate` — go to a URL

> 한글: `mcp__chrome-devtools__*`를 통해 사용 가능한 주요 도구:
> - `screenshot` — 현재 페이지 캡처
> - `evaluate` — 페이지 컨텍스트에서 JS 실행
> - `get_console_logs` — 콘솔 출력 가져오기
> - `get_network_requests` — 네트워크 트래픽 검사
> - `navigate` — URL로 이동

## MCP Permission Requests

When Claude calls an MCP tool and the user sees a permission prompt:

1. **Explain** what the tool does and why it's needed
2. **Ask** user to approve the prompt that appeared (or enable in settings)
3. **Wait** — do not retry until user confirms

```
Example message:
"Chrome DevTools MCP가 스크린샷 권한을 요청하고 있습니다.
나타난 허용 프롬프트를 승인해 주세요. 완료 후 알려주시면 계속하겠습니다."
```

> 한글: Claude가 MCP 도구를 호출할 때 사용자에게 권한 프롬프트가 표시되면:
>
> 1. **설명** — 해당 도구가 무엇을 하는지, 왜 필요한지 안내
> 2. **요청** — 표시된 허용 프롬프트를 승인하도록 (또는 설정에서 활성화) 요청
> 3. **대기** — 사용자가 확인할 때까지 재시도하지 않음

## Authentication Failure Pattern

### Step 1: Detect Auth Issue

Signs of auth failure:
- Screenshot shows a login / sign-in page
- Network request returns 401 or 403
- Console shows `Unauthorized`, `Session expired`, `Invalid token`
- Tool result indicates redirect to `/login`

> 한글: 인증 실패 징후:
> - 스크린샷에 로그인 / 로그인 페이지가 표시됨
> - 네트워크 요청이 401 또는 403 반환
> - 콘솔에 `Unauthorized`, `Session expired`, `Invalid token` 표시
> - 도구 결과가 `/login`으로의 리디렉션을 나타냄

### Step 2: Ask the User Which Auth Method

**STOP. Ask every time — never assume:**

```
이 페이지에 인증이 필요합니다. 어떤 방식으로 로그인하시겠어요?

1. 브라우저에서 직접 로그인 (Google OAuth, 아이디/비밀번호 등)
2. 이미 로그인된 브라우저에서 쿠키/세션 토큰 복사
3. 기타 (방식을 알려주세요)
```

Never handle raw credentials in conversation.

> 한글: **멈추고, 매번 확인하세요 — 절대 가정하지 마세요.**
>
> 대화에서 직접 자격 증명(비밀번호, 토큰 등)을 다루지 마세요.

### Step 3: Guide to Browser Login

**For browser-based login (OAuth, form):**

```
Chrome DevTools MCP 브라우저 창을 열고 아래 URL로 이동 후 직접 로그인해 주세요.
로그인 완료 후 알려주시면 계속 진행하겠습니다.
```

**For cookie/session injection:**
- Ask user to open their authenticated browser and copy the cookie value
- Provide exact DevTools steps: DevTools → Application → Cookies → copy value
- Do not ask for the value in chat if it's a sensitive token — guide them to paste it in the browser directly

> 한글: **브라우저 기반 로그인(OAuth, 폼)의 경우:**
> Chrome DevTools MCP 브라우저 창을 열고 해당 URL로 이동하여 직접 로그인하도록 안내하세요. 완료 후 알려달라고 요청하세요.
>
> **쿠키/세션 주입의 경우:**
> - 사용자에게 인증된 브라우저를 열고 쿠키 값을 복사하도록 요청
> - 정확한 DevTools 경로 안내: DevTools → Application → Cookies → 값 복사
> - 민감한 토큰이라면 채팅에서 값을 요청하지 말고, 브라우저에서 직접 붙여넣도록 안내

### Step 4: Verify Auth

After user confirms login:
1. Take a screenshot → confirm no login wall
2. Check console → no auth errors
3. Retry the original MCP tool call

> 한글: 사용자가 로그인 완료를 확인한 후:
> 1. 스크린샷 캡처 → 로그인 화면이 없음을 확인
> 2. 콘솔 확인 → 인증 오류 없음 확인
> 3. 원래 MCP 도구 호출 재시도

## Quick Reference

| Situation | Action |
|-----------|--------|
| MCP permission prompt | Explain → ask user to approve → wait → retry |
| Screenshot shows login page | Ask auth method → guide browser login → verify |
| 401/403 in network response | Ask auth method → guide accordingly → retry |
| Session expired mid-session | Guide re-login → verify screenshot → retry |
| Auth method unknown | Always ask — never assume |

> 한글: 상황별 대응:
> - MCP 권한 프롬프트: 설명 → 승인 요청 → 대기 → 재시도
> - 스크린샷에 로그인 페이지 표시: 인증 방식 확인 → 브라우저 로그인 안내 → 검증
> - 네트워크 응답 401/403: 인증 방식 확인 → 상황에 맞게 안내 → 재시도
> - 세션 중간 만료: 재로그인 안내 → 스크린샷 검증 → 재시도
> - 인증 방식 불명: 항상 확인 — 절대 가정 금지

## Security Boundaries

- **Never** ask for passwords, API keys, or tokens in the conversation
- **Never** use JavaScript execution to read `document.cookie`, `localStorage`, or session tokens
- **Always** guide users to perform auth actions directly in the browser window
- Auth state stays in the browser — Claude only verifies via screenshot and console

> 한글:
> - 대화에서 비밀번호, API 키, 토큰을 **절대** 요청하지 않음
> - JavaScript 실행으로 `document.cookie`, `localStorage`, 세션 토큰을 읽는 것을 **절대** 금지
> - 사용자가 인증 작업을 브라우저 창에서 직접 수행하도록 **항상** 안내
> - 인증 상태는 브라우저에 유지 — Claude는 스크린샷과 콘솔로만 확인

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Retrying MCP tool after auth error without checking | Screenshot first to confirm login state |
| Assuming OAuth when it might be session-based | Ask the user every time |
| Asking for password or token in chat | Guide to the browser window instead |
| Skipping screenshot verification after login | Always screenshot to confirm authenticated state |

> 한글: 자주 하는 실수와 해결책:
> - 인증 오류 후 확인 없이 MCP 도구 재시도: 먼저 스크린샷으로 로그인 상태 확인
> - 세션 기반일 수 있는데 OAuth로 가정: 매번 사용자에게 확인
> - 채팅에서 비밀번호 또는 토큰 요청: 대신 브라우저 창으로 안내
> - 로그인 후 스크린샷 검증 생략: 항상 스크린샷으로 인증 상태 확인

## Workflow

```
MCP tool needed
    │
    ├── Permission denied / not approved?
    │       └── Explain → Ask user to approve prompt → Wait → Retry
    │
    └── Auth error / login page detected?
            │
            ├── Ask: "어떤 인증 방식인가요?"
            ├── Guide to browser window (or cookie copy steps)
            ├── Wait for user confirmation
            ├── Screenshot → verify authenticated state
            └── Retry original MCP tool call
```

> 한글: MCP 도구 필요 → 권한 거부/미승인 시: 설명 → 승인 요청 → 대기 → 재시도 / 인증 오류·로그인 페이지 감지 시: 인증 방식 확인 → 브라우저 창(또는 쿠키 복사 단계)으로 안내 → 사용자 확인 대기 → 스크린샷으로 인증 상태 검증 → 원래 MCP 도구 호출 재시도
