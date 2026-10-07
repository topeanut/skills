#!/usr/bin/env python3
"""Show GA/Firebase events from the Cashdoc and Cashwalk Android apps as they fire.

Connect an Android device (USB debugging on) and run:

    python3 ga_logcat.py                 # wait for a device, stream events live
    python3 ga_logcat.py --only more_button,detail_click
    python3 ga_logcat.py --dump          # print events already in the logcat buffer and exit

Sources read from `adb logcat`:
  - Cashwalk bridge log   CASHWALK-LOG  "fireBaseEvent = <name> / {json}"
  - Cashdoc tester log    TESTER_LOG    "sendLog -> <name>" + "\tkey=value(Type)" lines
  - Firebase SDK log      FA-SVC        "Logging event: origin=app,name=...,params=Bundle[{...}]"
    (enabled by this script via `setprop log.tag.FA-SVC VERBOSE`; shown only when no
    bridge/tester line reported the same event, e.g. release builds)

Ctrl-C restores the device properties this script changed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import select
import shutil
import signal
import subprocess
import sys
import time

APPS = {
    "com.cashdoc.cashdoc": "캐시닥",
    "com.cashwalk.cashwalk": "캐시워크",
}
# Params that add noise to the one-line view (still shown with --full).
NOISY_KEYS = {
    "page_location",
    "page_path",
    "medium",
    "page_title",
    "page_referrer",
}
DEFAULT_HIDE = r"^debug_"

LINE_RE = re.compile(
    r"^(\d\d-\d\d) (\d\d:\d\d:\d\d\.\d+) ([VDIWEF])/(.+?)\(\s*(\d+)\): ?(.*)$"
)
CW_BRIDGE_RE = re.compile(r"fireBaseEvent = (\S+) / (\{.*)$")
TESTER_START_RE = re.compile(r"sendLog -> (\S+)\s*$")
TESTER_PARAM_RE = re.compile(r"^\t([A-Za-z0-9_]+)=(.*?)(?:\((?:String|Long|Integer|Double|Boolean|Float)\))?$")
FA_EVENT_RE = re.compile(r"Logging event: origin=(\w+),name=([^,]+),params=Bundle\[\{(.*)\}\]")
FA_PARAM_RE = re.compile(r"([A-Za-z0-9_]+)(?:\([^)]*\))?=(.*?)(?=, [A-Za-z0-9_]+(?:\([^)]*\))?=|$)")

USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def find_adb() -> str:
    adb = shutil.which("adb")
    if adb:
        return adb
    fallback = os.path.expanduser("~/Library/Android/sdk/platform-tools/adb")
    if os.path.exists(fallback):
        return fallback
    sys.exit("adb를 찾지 못했습니다. Android platform-tools를 설치하세요 (brew install android-platform-tools).")


class Device:
    def __init__(self, adb: str, serial: str | None):
        self.adb = adb
        self.serial = serial

    def cmd(self, *args: str) -> list[str]:
        base = [self.adb]
        if self.serial:
            base += ["-s", self.serial]
        return base + list(args)

    def shell(self, *args: str) -> str:
        out = subprocess.run(self.cmd("shell", *args), capture_output=True, text=True)
        return out.stdout.strip()


def pick_serial(adb: str, wanted: str | None) -> str:
    announced = False
    while True:
        out = subprocess.run([adb, "devices"], capture_output=True, text=True).stdout
        serials = [l.split()[0] for l in out.splitlines()[1:] if l.strip().endswith("device")]
        if wanted:
            if wanted in serials:
                return wanted
        elif len(serials) == 1:
            return serials[0]
        elif len(serials) > 1:
            sys.exit("기기가 여러 대입니다. --serial 로 하나를 고르세요: " + ", ".join(serials))
        if not announced:
            print(color("기기 연결 대기 중… (USB 디버깅을 켜고 연결하세요)", "33"), flush=True)
            announced = True
        time.sleep(1)


class PidMap:
    def __init__(self, device: Device):
        self.device = device
        self.map: dict[str, str] = {}
        self.at = 0.0

    def name(self, pid: str) -> str | None:
        if pid not in self.map and time.time() - self.at > 2:
            self.refresh()
        return self.map.get(pid)

    def refresh(self) -> None:
        self.at = time.time()
        for pkg, label in APPS.items():
            for pid in self.device.shell("pidof", pkg).split():
                self.map[pid] = label


class Printer:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.only = [s for s in (args.only or "").split(",") if s]
        self.hide = re.compile(args.hide) if args.hide else None
        self.recent: list[tuple[float, str]] = []  # (log time in seconds, key) of bridge events

    def _key(self, name: str, params: dict) -> str:
        return f"{name}|{params.get('event_label', '')}"

    def emit(self, ts: str, app: str, name: str, params: dict, source: str) -> None:
        key = self._key(name, params)
        h, m, sec = ts.split(":")
        now = int(h) * 3600 + int(m) * 60 + float(sec)  # log time, so --dump dedupes correctly
        self.recent = [(t, k) for t, k in self.recent if 0 <= now - t < 3]
        if source == "firebase":
            if any(k == key for _, k in self.recent):
                return  # already shown from the app's own bridge/tester log
        else:
            self.recent.append((now, key))

        label = str(params.get("event_label", ""))
        title = label or name
        if self.hide and (self.hide.search(title) or self.hide.search(name)):
            return
        if self.only and not any(o in title or o in name for o in self.only):
            return

        if self.args.json:
            print(json.dumps({"time": ts, "app": app, "event": name, "source": source, "params": params}, ensure_ascii=False), flush=True)
            return

        shown = {
            k: v
            for k, v in params.items()
            if k != "event_label" and not k.startswith("ga_") and (self.args.full or k not in NOISY_KEYS)
        }
        parts = " ".join(f"{k}={v}" for k, v in shown.items())
        app_col = {"캐시닥": "36", "캐시워크": "32"}.get(app, "35")
        head = f"{ts}  {color(app.ljust(5), app_col)}  {color(title, '1')}"
        if label and name != "cashdoc_event":
            head += color(f" ({name})", "2")
        print(f"{head}  {parts}", flush=True)


class Parser:
    def __init__(self, pids: PidMap, printer: Printer):
        self.pids = pids
        self.printer = printer
        self.pending: dict[str, dict] = {}  # TESTER_LOG multi-line events per pid

    def flush(self, pid: str | None = None) -> None:
        for p in [pid] if pid else list(self.pending):
            ev = self.pending.pop(p, None)
            if ev:
                self.printer.emit(ev["ts"], ev["app"], ev["name"], ev["params"], "tester")

    def feed(self, line: str) -> None:
        m = LINE_RE.match(line.rstrip("\r\n"))
        if not m:
            return
        _, ts, _, tag, pid, msg = m.groups()
        tag = tag.strip()

        if pid in self.pending and not (tag == "TESTER_LOG" and TESTER_PARAM_RE.match(msg)):
            self.flush(pid)

        if tag == "TESTER_LOG":
            start = TESTER_START_RE.search(msg)
            if start:
                self.pending[pid] = {
                    "ts": ts,
                    "app": self.pids.name(pid) or "캐시닥",
                    "name": start.group(1),
                    "params": {},
                }
                return
            param = TESTER_PARAM_RE.match(msg)
            if param and pid in self.pending:
                self.pending[pid]["params"][param.group(1)] = param.group(2)
            return

        if tag == "CASHWALK-LOG":
            bridge = CW_BRIDGE_RE.search(msg)
            if bridge:
                try:
                    params = json.loads(bridge.group(2))
                except json.JSONDecodeError:
                    params = {"raw": bridge.group(2)}
                self.printer.emit(ts, self.pids.name(pid) or "캐시워크", bridge.group(1), params, "bridge")
            return

        if tag == "FA-SVC":
            fa = FA_EVENT_RE.search(msg)
            if fa and fa.group(1) == "app":
                params = {k: v for k, v in FA_PARAM_RE.findall(fa.group(3))}
                self.printer.emit(ts, "Firebase", fa.group(2), params, "firebase")


def set_props(device: Device, debug_app: str | None) -> dict[str, str]:
    before = {}
    props = {"log.tag.FA": "VERBOSE", "log.tag.FA-SVC": "VERBOSE"}
    if debug_app:
        props["debug.firebase.analytics.app"] = debug_app
    for key, value in props.items():
        before[key] = device.shell("getprop", key)
        device.shell("setprop", key, value)
    return before


def restore_props(device: Device, before: dict[str, str]) -> None:
    for key, value in before.items():
        if key == "debug.firebase.analytics.app" and not value:
            value = ".none."
        device.shell("setprop", key, value if value else "''")


def print_guide(device: Device, model: str, running: set[str], debug_app: str | None) -> None:
    """Explain on startup how events are caught and how to read the output."""
    dim = lambda t: color(t, "2")
    lines = [
        color(f"● {model} ({device.serial}) 연결됨 · 실행 중 앱: {', '.join(sorted(running)) or '없음'}", "33"),
        "",
        color("어떻게 잡나요?", "1"),
        "  웹뷰에서 GA가 나가면 앱이 네이티브 브릿지로 받아 Firebase에 넘기고, 그 과정이 기기 로그(logcat)에 남습니다.",
        "  이 도구는 adb logcat을 실시간으로 읽어 아래 세 가지 로그에서 GA 이벤트만 골라 한 줄로 보여줍니다.",
        f"    {color('캐시워크', '32')}  CASHWALK-LOG  FirebaseEventBridgeDelegate · fireBaseEvent = <이벤트> / {{파라미터 JSON}}",
        f"    {color('캐시닥', '36')}    TESTER_LOG    DebugLog · sendLog -> <이벤트> + 줄마다 key=value (테스트 빌드)",
        f"    {color('Firebase', '35')}  FA-SVC        Logging event: name=…, params=Bundle[…] (운영 빌드 대비, 앱 구분 불가)",
        "  앱은 로그를 남긴 프로세스 PID로 구분하고, 같은 이벤트가 두 로그에 찍히면 한 번만 보여줍니다.",
        "",
        color("기기에서 바꾼 설정 (Ctrl-C로 끝내면 원래대로 되돌림)", "1"),
        "  setprop log.tag.FA VERBOSE, log.tag.FA-SVC VERBOSE  → Firebase SDK가 이벤트마다 로그를 남김",
    ]
    if debug_app:
        lines.append(f"  setprop debug.firebase.analytics.app {debug_app}  → 즉시 전송 + Firebase DebugView 표시")
    lines += [
        "",
        color("읽는 법", "1"),
        f"  {dim('시각')}  {dim('앱')}  {color('event_label', '1')}  {dim('주요 파라미터(page_location 등은 --full)')}",
        "  여기 찍히면 웹뷰 → 앱 브릿지까지 전달된 것입니다. GA4 서버 도착은 Firebase DebugView나 다음 날 BigQuery로 확인하세요.",
        "  연타 제한 확인: 여러 번 눌렀는데 한 줄만 찍히면 제한이 동작한 것입니다.",
        dim("  옵션: --only 문자열,…  --full  --json  --dump  --debug-app 패키지  --quiet(이 안내 생략)  -h"),
        "",
        color("GA 이벤트 대기 중… (Ctrl-C 종료)", "33"),
    ]
    print("\n".join(lines), flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="캐시닥·캐시워크 Android 앱 GA 이벤트 실시간 보기")
    ap.add_argument("--serial", help="adb 기기 시리얼 (여러 대 연결 시)")
    ap.add_argument("--only", help="event_label/이벤트명에 포함될 문자열, 쉼표 구분 (예: more_button,detail_click)")
    ap.add_argument("--hide", default=DEFAULT_HIDE, help=f"숨길 event_label 정규식 (기본 {DEFAULT_HIDE!r}, 빈 값이면 전부 표시)")
    ap.add_argument("--full", action="store_true", help="page_location 등 긴 파라미터도 표시")
    ap.add_argument("--json", action="store_true", help="이벤트를 JSON 한 줄씩 출력")
    ap.add_argument("--dump", action="store_true", help="기기 logcat 버퍼에 이미 있는 이벤트만 출력하고 종료")
    ap.add_argument("--debug-app", help="Firebase 즉시 전송·DebugView 대상 패키지 (예: com.cashdoc.cashdoc)")
    ap.add_argument("--keep-props", action="store_true", help="종료할 때 기기 setprop 을 되돌리지 않음")
    ap.add_argument("--quiet", action="store_true", help="시작할 때 동작 안내를 생략")
    args = ap.parse_args()

    adb = find_adb()
    device = Device(adb, pick_serial(adb, args.serial))
    model = device.shell("getprop", "ro.product.model")
    pids = PidMap(device)
    pids.refresh()
    printer = Printer(args)
    parser = Parser(pids, printer)

    if args.dump:
        out = subprocess.run(device.cmd("logcat", "-d", "-v", "time"), capture_output=True, text=True, errors="replace").stdout
        for line in out.splitlines():
            parser.feed(line)
        parser.flush()
        return

    before = set_props(device, args.debug_app)
    running = set(pids.map.values())
    if args.quiet:
        print(color(f"● {model} ({device.serial}) 연결됨 — GA 이벤트 대기 중. 실행 중 앱: {', '.join(sorted(running)) or '없음'} (Ctrl-C 종료)", "33"), flush=True)
    else:
        print_guide(device, model, running, args.debug_app)

    proc = subprocess.Popen(device.cmd("logcat", "-T", "1", "-v", "time"), stdout=subprocess.PIPE, text=True, errors="replace", bufsize=1)

    def stop(*_):
        proc.terminate()
        parser.flush()
        if not args.keep_props:
            restore_props(device, before)
            print(color("\n기기 Firebase 로그 설정을 되돌렸습니다.", "33"), flush=True)
        sys.exit(0)

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    assert proc.stdout is not None
    while True:
        ready, _, _ = select.select([proc.stdout], [], [], 0.3)
        if not ready:
            parser.flush()  # TESTER_LOG event finished (no more param lines)
            if proc.poll() is not None:
                print(color("logcat 연결이 끊겼습니다 (기기 분리?). 다시 연결하면 재시작하세요.", "31"), flush=True)
                stop()
            continue
        line = proc.stdout.readline()
        if not line:
            continue
        parser.feed(line)


if __name__ == "__main__":
    main()
