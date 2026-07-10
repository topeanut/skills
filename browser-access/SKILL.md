---
name: browser-access
description: Use when starting any browser-based task — UI verification, visual testing, network debugging, dev server inspection, or live DOM inspection. Prefer Claude in Chrome; fall back to Chrome DevTools MCP. Also use when a browser MCP fails, returns 401/403, shows a login page, or when MCP permissions need to be granted.
---

# Browser Access

## Overview

Two browser MCPs are available. **Default to Claude in Chrome (`mcp__claude-in-chrome__*`).** Reach for Chrome DevTools MCP (`mcp__chrome-devtools__*`) only for the instrumentation it uniquely provides, or when Claude in Chrome is unavailable.

**Why Claude in Chrome first:** it attaches to the user's real Chrome profile. Cookies and sessions are already there, so authenticated pages just work — no `--remote-debugging-port` restart, no login dance.

**Core principle:** Authentication state lives in the browser. The user performs login; Claude only verifies the result.

> 한글: 브라우저 MCP는 두 가지입니다. **기본은 Claude in Chrome (`mcp__claude-in-chrome__*`)**. Chrome DevTools MCP (`mcp__chrome-devtools__*`)는 그것만 가능한 계측 작업이거나 Claude in Chrome을 쓸 수 없을 때만 사용하세요.
>
> **Claude in Chrome을 우선하는 이유:** 사용자의 실제 Chrome 프로필에 붙습니다. 쿠키·세션이 이미 있으므로 인증이 필요한 페이지가 그냥 열립니다 — `--remote-debugging-port` 재시작도, 로그인 절차도 불필요.
>
> **핵심 원칙:** 인증 상태는 브라우저에 존재합니다. 로그인은 사용자가 직접 수행하고, Claude는 결과만 확인합니다.

## Which MCP to Use

| Task | Use |
|------|-----|
| Open a page, click, type, fill a form | Claude in Chrome |
| Screenshot / visual check | Claude in Chrome |
| Read page text or DOM | Claude in Chrome |
| Console logs, network requests (what happened) | Claude in Chrome |
| Anything behind a login | Claude in Chrome |
| Record a GIF of a flow | Claude in Chrome |
| Performance trace / Core Web Vitals | Chrome DevTools |
| Heap snapshot / memory profiling | Chrome DevTools |
| Lighthouse audit | Chrome DevTools |
| Device emulation, CPU/network throttling | Chrome DevTools |
| Detailed network timing per request | Chrome DevTools |
| Claude in Chrome unavailable or extension not installed | Chrome DevTools (fallback) |

Rule of thumb: **driving the page → Claude in Chrome. Measuring the page → Chrome DevTools.**

> 한글: 판단 기준 — **페이지를 조작하면 Claude in Chrome, 페이지를 계측하면 Chrome DevTools.**
>
> Claude in Chrome: 페이지 열기/클릭/입력/폼, 스크린샷, DOM·텍스트 읽기, 콘솔·네트워크 확인, 로그인 필요한 모든 것, GIF 녹화.
> Chrome DevTools: 성능 트레이스, Core Web Vitals, 힙 스냅샷, Lighthouse, 디바이스 에뮬레이션·스로틀링, 요청별 상세 타이밍, 그리고 Claude in Chrome을 못 쓸 때의 폴백.

## Primary Path: Claude in Chrome

### Step 1: Invoke the `claude-in-chrome` skill first

Always invoke the `claude-in-chrome` skill **before** calling any `mcp__claude-in-chrome__*` tool. It carries the current usage rules.

### Step 2: Load tools in ONE ToolSearch call

The tools are deferred — their schemas must be loaded before use. Batch them; each separate `ToolSearch` call costs a round-trip.

```
ToolSearch query:
select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__tabs_create_mcp
```

Add task-specific tools to that same call when you already know you need them: `read_console_messages`, `read_network_requests`, `form_input`, `gif_creator`, `javascript_tool`.

### Step 3: Get tab context before creating tabs

Call `tabs_context_mcp` first to see the user's open tabs. Then:
- Reuse an existing tab **only** if the user explicitly asked for it
- Otherwise create a new tab with `tabs_create_mcp`
- Never reuse tab IDs from a previous session

### Step 4: Do the work

| Need | Tool |
|------|------|
| Go to a URL | `navigate` |
| Click, type, scroll, screenshot | `computer` |
| Read structured page content | `read_page` / `get_page_text` |
| Locate an element | `find` |
| Fill a form field | `form_input` |
| Console output (supports `pattern` regex filter) | `read_console_messages` |
| Network traffic | `read_network_requests` |
| Run JS in the page | `javascript_tool` |
| Record the flow | `gif_creator` |

> 한글: **주 경로 — Claude in Chrome**
>
> 1. `mcp__claude-in-chrome__*` 도구를 호출하기 **전에** 반드시 `claude-in-chrome` 스킬을 먼저 실행하세요.
> 2. 도구는 deferred 상태입니다. **ToolSearch 한 번에 모아서** 로드하세요 — 개별 호출은 왕복 비용만 낭비합니다. 필요한 게 확실하면 `read_console_messages`, `read_network_requests`, `form_input`, `gif_creator`, `javascript_tool`도 같은 호출에 넣으세요.
> 3. 탭 만들기 전에 `tabs_context_mcp`로 현재 탭 확인. 사용자가 명시적으로 요청한 경우에만 기존 탭 재사용, 아니면 `tabs_create_mcp`로 새 탭. 이전 세션의 탭 ID는 절대 재사용 금지.
> 4. 작업 수행 (위 표 참고).

### Site Permissions

Claude in Chrome needs site-level permission, granted in the extension. If a tool call is blocked:

1. **Explain** what you are trying to do and on which site
2. **Ask** the user to allow that site in the Claude in Chrome extension
3. **Wait** — do not retry until the user confirms

> 한글: Claude in Chrome은 확장 프로그램에서 사이트별 권한이 필요합니다. 차단되면: 무엇을 어느 사이트에서 하려는지 **설명** → 확장에서 해당 사이트 허용을 **요청** → 사용자 확인까지 **대기**. 확인 전 재시도 금지.

### Do Not Trigger Dialogs

`alert`, `confirm`, `prompt`, and browser modals **block all further browser events** — the extension stops receiving commands. If you trigger one, the user must dismiss it manually.

- Avoid clicking elements that open confirmation dialogs (e.g. "Delete")
- If you must, warn the user first
- Use `console.log` + `read_console_messages` for debugging, never `alert`

> 한글: `alert`/`confirm`/`prompt`/모달은 **이후 모든 브라우저 이벤트를 차단**합니다. 확장이 명령을 못 받습니다. 확인 다이얼로그를 여는 요소(예: "삭제") 클릭을 피하고, 불가피하면 사용자에게 먼저 경고하세요. 디버깅은 `alert` 대신 `console.log` + `read_console_messages`.

## Fallback Path: Chrome DevTools MCP

Use when the task needs DevTools-only instrumentation, or when Claude in Chrome is unavailable.

### Connection Check

1. Call any `mcp__chrome-devtools__*` tool (e.g. `list_pages`)
2. Succeeds → proceed
3. Fails → Chrome must be running with remote debugging enabled:

```bash
# Mac
open -a "Google Chrome" --args --remote-debugging-port=9222

# Or if Chrome is already open, restart with:
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

Then retry the tool call.

> 한글: **폴백 경로 — Chrome DevTools MCP.** DevTools에서만 되는 계측 작업이거나 Claude in Chrome을 쓸 수 없을 때 사용.
>
> 연결 확인: `mcp__chrome-devtools__*` 아무 도구(예: `list_pages`) 호출 → 성공하면 진행 → 실패하면 위 명령으로 원격 디버깅 활성화 상태로 Chrome 실행 후 재시도.

### Tool Reference

Actual tool names under `mcp__chrome-devtools__*` (there are also numbered instances — `chrome-devtools-2` … `chrome-devtools-5` — for parallel page inspection):

| Purpose | Tool |
|---------|------|
| Capture page | `take_screenshot` |
| Run JS in page context | `evaluate_script` |
| Console output | `list_console_messages`, `get_console_message` |
| Network traffic | `list_network_requests`, `get_network_request` |
| Navigate | `navigate_page` |
| Page management | `new_page`, `list_pages`, `select_page`, `close_page` |
| Interact | `click`, `fill`, `fill_form`, `hover`, `type_text`, `press_key`, `drag` |
| Accessibility tree | `take_snapshot` |
| Performance | `performance_start_trace`, `performance_stop_trace`, `performance_analyze_insight` |
| Memory | `take_heapsnapshot` |
| Audit | `lighthouse_audit` |
| Emulation | `emulate`, `resize_page` |
| Wait for condition | `wait_for` |

> 한글: `mcp__chrome-devtools__*`의 실제 도구명은 위 표와 같습니다. 병렬 페이지 검사를 위해 `chrome-devtools-2` ~ `chrome-devtools-5` 인스턴스도 존재합니다.

### MCP Permission Requests

When Claude calls an MCP tool and the user sees a permission prompt:

1. **Explain** what the tool does and why it's needed
2. **Ask** the user to approve the prompt that appeared (or enable it in settings)
3. **Wait** — do not retry until the user confirms

```
Example message:
"Chrome DevTools MCP가 스크린샷 권한을 요청하고 있습니다.
나타난 허용 프롬프트를 승인해 주세요. 완료 후 알려주시면 계속하겠습니다."
```

> 한글: MCP 권한 프롬프트가 뜨면: 도구가 무엇을 하고 왜 필요한지 **설명** → 프롬프트 승인(또는 설정에서 활성화)을 **요청** → 사용자 확인까지 **대기**.

## Authentication Failure Pattern

With Claude in Chrome this should be rare — the user's session is already loaded. If it still happens (logged out, expired session, wrong profile), or you are on the DevTools fallback path:

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
브라우저 창에서 아래 URL로 이동 후 직접 로그인해 주세요.
로그인 완료 후 알려주시면 계속 진행하겠습니다.
```

**For cookie/session injection:**
- Ask the user to open their authenticated browser and copy the cookie value
- Provide exact steps: DevTools → Application → Cookies → copy value
- Do not ask for the value in chat if it's a sensitive token — guide them to paste it in the browser directly

### Step 4: Verify Auth

After the user confirms login:
1. Take a screenshot → confirm no login wall
2. Check console → no auth errors
3. Retry the original tool call

> 한글: **인증 실패 대응.** Claude in Chrome에서는 세션이 이미 로드되어 있어 드뭅니다. 그래도 발생하면(로그아웃, 세션 만료, 다른 프로필) 또는 DevTools 폴백 경로라면:
>
> 1. **감지** — 스크린샷에 로그인 페이지, 401/403 응답, 콘솔의 `Unauthorized`·`Session expired`·`Invalid token`, `/login` 리디렉션.
> 2. **인증 방식 확인** — 멈추고, 매번 물어보세요. 절대 가정 금지. 대화에서 자격 증명(비밀번호, 토큰)을 직접 다루지 마세요.
> 3. **브라우저 로그인 안내** — OAuth·폼이면 브라우저 창에서 직접 로그인 요청. 쿠키/세션이면 DevTools → Application → Cookies → 값 복사 경로 안내, 민감한 토큰은 채팅에 요청하지 말고 브라우저에 직접 붙여넣도록.
> 4. **검증** — 스크린샷으로 로그인 화면 없음 확인 → 콘솔에 인증 오류 없음 확인 → 원래 도구 호출 재시도.

## Avoid Rabbit Holes

Stop and ask the user for guidance when:
- Browser tool calls fail or error 2–3 times in a row
- No response from the extension / MCP
- Page elements don't respond to clicks or input
- Pages don't load or time out

Explain what you attempted, what went wrong, and ask how to proceed. Do not retry the same failing action or wander into unrelated pages.

> 한글: 다음 상황이면 멈추고 사용자에게 물어보세요 — 도구 호출이 2~3회 연속 실패, 확장/MCP 무응답, 요소가 클릭·입력에 반응 없음, 페이지 로드 실패·타임아웃. 시도한 것과 실패 내용을 설명하고 진행 방법을 확인하세요. 같은 실패 동작 반복이나 무관한 페이지 탐색 금지.

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
| Reaching for Chrome DevTools by habit | Default to Claude in Chrome; DevTools is for measurement and fallback |
| Calling `mcp__claude-in-chrome__*` before invoking the `claude-in-chrome` skill | Invoke the skill first |
| One `ToolSearch` call per tool | Batch every expected tool into a single `select:` query |
| Creating a tab without checking `tabs_context_mcp` | Get tab context first |
| Restarting Chrome with `--remote-debugging-port` for a Claude in Chrome task | That flag is only for the DevTools fallback |
| Clicking a button that opens a `confirm()` dialog | It freezes the extension — avoid, or warn the user first |
| Retrying after an auth error without checking | Screenshot first to confirm login state |
| Assuming OAuth when it might be session-based | Ask the user every time |
| Asking for a password or token in chat | Guide to the browser window instead |

> 한글: 자주 하는 실수 —
> 습관적으로 Chrome DevTools 사용(기본은 Claude in Chrome, DevTools는 계측·폴백) / `claude-in-chrome` 스킬 실행 전에 도구 호출 / 도구마다 `ToolSearch` 개별 호출(하나로 묶을 것) / `tabs_context_mcp` 확인 없이 탭 생성 / Claude in Chrome 작업인데 `--remote-debugging-port`로 Chrome 재시작(그 플래그는 DevTools 폴백 전용) / `confirm()` 다이얼로그 여는 버튼 클릭(확장 멈춤) / 확인 없이 인증 오류 후 재시도 / 세션 기반일 수 있는데 OAuth로 가정 / 채팅에서 비밀번호·토큰 요청.

## Workflow

```
Browser task
    │
    ├── Needs perf trace / heap / Lighthouse / emulation / detailed timing?
    │       └── Chrome DevTools MCP → connection check → run
    │
    └── Everything else → Claude in Chrome
            │
            ├── Invoke `claude-in-chrome` skill
            ├── ONE ToolSearch call → load all needed tools
            ├── tabs_context_mcp → reuse only if user asked, else tabs_create_mcp
            ├── Do the work
            │
            ├── Site permission blocked?
            │       └── Explain → ask user to allow site → wait → retry
            │
            ├── Auth error / login page?
            │       └── Ask auth method → guide browser login → screenshot verify → retry
            │
            ├── Claude in Chrome unavailable?
            │       └── Fall back to Chrome DevTools MCP
            │
            └── 2–3 failures in a row? → stop, report, ask user
```

> 한글: 브라우저 작업 → 성능 트레이스·힙·Lighthouse·에뮬레이션·상세 타이밍이면 Chrome DevTools(연결 확인 후 실행). 그 외 전부 Claude in Chrome → `claude-in-chrome` 스킬 실행 → ToolSearch 한 번에 도구 로드 → `tabs_context_mcp` 확인 후 탭 생성 → 작업 수행. 사이트 권한 차단 시 설명·요청·대기·재시도 / 인증 오류 시 방식 확인·로그인 안내·스크린샷 검증·재시도 / Claude in Chrome 불가 시 DevTools 폴백 / 2~3회 연속 실패 시 중단하고 사용자에게 보고.
