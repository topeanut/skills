---
name: chrome-devtools-mcp-auth
description: Use when starting any browser-based task — UI verification, visual testing, network debugging, dev server inspection, or live DOM inspection. Also use when Chrome DevTools MCP fails, returns 401/403, shows a login page, or when MCP permissions need to be granted.
---

# Chrome DevTools MCP with Authentication

## Overview

Chrome DevTools MCP gives Claude a live browser window. Use it proactively for any browser-related task, not just when errors occur.

**Core principle:** Authentication state lives in the browser. The user performs login; Claude only verifies the result.

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

## MCP Tool Reference

Common tools available via `mcp__chrome-devtools__*`:
- `screenshot` — capture current page
- `evaluate` — run JS in page context
- `get_console_logs` — fetch console output
- `get_network_requests` — inspect network traffic
- `navigate` — go to a URL

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

## Authentication Failure Pattern

### Step 1: Detect Auth Issue

Signs of auth failure:
- Screenshot shows a login / sign-in page
- Network request returns 401 or 403
- Console shows `Unauthorized`, `Session expired`, `Invalid token`
- Tool result indicates redirect to `/login`

### Step 2: Ask the User Which Auth Method

**STOP. Ask every time — never assume:**

```
이 페이지에 인증이 필요합니다. 어떤 방식으로 로그인하시겠어요?

1. 브라우저에서 직접 로그인 (Google OAuth, 아이디/비밀번호 등)
2. 이미 로그인된 브라우저에서 쿠키/세션 토큰 복사
3. 기타 (방식을 알려주세요)
```

Never handle raw credentials in conversation.

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

### Step 4: Verify Auth

After user confirms login:
1. Take a screenshot → confirm no login wall
2. Check console → no auth errors
3. Retry the original MCP tool call

## Quick Reference

| Situation | Action |
|-----------|--------|
| MCP permission prompt | Explain → ask user to approve → wait → retry |
| Screenshot shows login page | Ask auth method → guide browser login → verify |
| 401/403 in network response | Ask auth method → guide accordingly → retry |
| Session expired mid-session | Guide re-login → verify screenshot → retry |
| Auth method unknown | Always ask — never assume |

## Security Boundaries

- **Never** ask for passwords, API keys, or tokens in the conversation
- **Never** use JavaScript execution to read `document.cookie`, `localStorage`, or session tokens
- **Always** guide users to perform auth actions directly in the browser window
- Auth state stays in the browser — Claude only verifies via screenshot and console

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Retrying MCP tool after auth error without checking | Screenshot first to confirm login state |
| Assuming OAuth when it might be session-based | Ask the user every time |
| Asking for password or token in chat | Guide to the browser window instead |
| Skipping screenshot verification after login | Always screenshot to confirm authenticated state |

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
