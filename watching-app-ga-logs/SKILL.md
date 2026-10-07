---
name: watching-app-ga-logs
description: Use when checking whether GA/Firebase events fire inside the Cashdoc or Cashwalk Android app (webview bridge events such as cashdoc_event, cashdoc_detail_more_button, cashdoc_hospital_detail_click), when the user connects an Android test device to verify GA, or asks "앱에서 GA 확인", "앱 GA 로그", "GA 찍히는지 봐줘".
---

# Watching App GA Logs

## Overview

`scripts/ga_logcat.py` streams GA events from a USB-connected Android device to the **user's own terminal**, one line per event, as they fire. The user runs it and watches; the agent does not need to tail logcat itself.

> 한글: `scripts/ga_logcat.py`는 USB로 연결한 Android 기기의 GA 이벤트를 **사용자 터미널**에 한 줄씩 실시간으로 띄운다. 사용자가 직접 실행해 보고, 에이전트가 logcat을 대신 감시할 필요는 없다.

## Run

Give the user this command (their terminal, not a background task):

```bash
python3 ~/.claude/skills/watching-app-ga-logs/scripts/ga_logcat.py
```

It waits for a device, turns on Firebase verbose logging (`setprop log.tag.FA/FA-SVC VERBOSE`), prints events, and restores those properties on Ctrl-C.

| Option | Use |
|---|---|
| `--only more_button,detail_click` | show only labels/names containing these strings |
| `--hide ''` | also show `debug_*` events (hidden by default) |
| `--full` | include `page_location`, `page_path`, `medium` |
| `--json` | one JSON object per event |
| `--dump` | print events already in the logcat buffer, then exit (agent-friendly check) |
| `--debug-app com.cashdoc.cashdoc` | also enable Firebase immediate upload / DebugView for that app |
| `--serial <id>` | pick a device when several are connected |

Output: `13:49:20.132  캐시닥  cashdoc_detail_more_button  tab=hospital_info button_name=review`

> 한글: 위 명령을 사용자 터미널에서 실행하게 안내한다. 기기 연결을 기다렸다가 Firebase 로그를 켜고 이벤트를 출력하며, Ctrl-C로 끝내면 기기 설정을 되돌린다. 에이전트가 사후 확인만 할 때는 `--dump`를 쓴다.

## Where events come from

| App build | Log the tool reads | App attribution |
|---|---|---|
| Cashwalk (`com.cashwalk.cashwalk`) | `CASHWALK-LOG` `FirebaseEventBridgeDelegate … fireBaseEvent = <name> / {json}` | by PID |
| Cashdoc test build (`com.cashdoc.cashdoc`) | `TESTER_LOG` `DebugLog sendLog -> <name>` + `\tkey=value(Type)` lines | by PID |
| Any build | `FA-SVC Logging event: origin=app,name=…` (Google Play services process) | shown as `Firebase`; skipped when a bridge/tester line already showed the same event |

A bridge/tester line proves webview → native bridge delivery. It does not prove the upload reached GA4; for that use Firebase DebugView (`--debug-app`) or next-day BigQuery.

> 한글: 브릿지/테스터 로그는 웹뷰→네이티브 전달까지 증명한다. GA4 서버 도착은 DebugView(`--debug-app`)나 다음 날 BigQuery로 확인한다. 캐시닥 테스트 빌드는 FA-SVC에 cashdoc_event가 안 찍히고 TESTER_LOG에만 남는다.

## Verifying a throttle or a fix

Compare taps with events: in `adb logcat -d -v time`, `Delivering touch to (<pid>): action: 0x1` lines are tap releases. N rapid taps → 1 event = throttle works.

> 한글: 연타 제한 검증은 터치 해제 로그(`action: 0x1`) 개수와 이벤트 개수를 시각으로 대조한다.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `기기 연결 대기 중…` never ends | USB debugging off, or device `unauthorized` — accept the prompt on the phone |
| Nothing prints while tapping | app not using the expected log (release build) → rely on `FA-SVC`; confirm the app is on the screen you think (PID shown in startup line) |
| iOS | not supported (no logcat); use Xcode `-FIRDebugEnabled` + Firebase DebugView |
