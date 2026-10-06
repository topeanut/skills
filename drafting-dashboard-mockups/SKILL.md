---
name: drafting-dashboard-mockups
description: Use when a lead asks for a chart draft, dashboard mockup or "차트 초안" before a Cashdoc Evidence dashboard exists, when real BigQuery numbers and not-yet-tracked metrics must appear on one reviewable page, or when an HTML mockup will later become an Evidence page.
---

# Drafting Dashboard Mockups

## Overview
The mockup is the spec for the GA events, the Prefect producer and the Evidence page that follow. A good one is reproducible (data re-pulled with one command), shows only numbers the future pipeline can produce, and maps every widget to the metric it will become. A pretty page with hard-coded numbers is a dead end.

> 한글: 목업은 이후 GA·Prefect·Evidence의 명세다. 한 명령으로 데이터를 다시 뽑을 수 있고, 이후 파이프라인이 실제로 만들 수 있는 숫자만 보여 주고, 위젯마다 나중의 지표 이름이 붙어 있어야 한다. 숫자를 박아 넣은 예쁜 페이지는 막다른 길이다.

## Deliverable layout
```
<name>-dashboard/
  <name>-dashboard.html        # renders sample data if no data, real data if present
  sql/<name>_probe.sql         # exploration: which labels/params exist
  sql/<name>_daily.sql         # main query, one row per date × dimension (the JSON contract)
  scripts/fetch-<name>-data.sh # bq query → <name>-data.json → <name>-dashboard-YYYYMMDD.html (data embedded)
  README.md                    # files, JSON shape, how to refresh, open questions
```
- Embed data via `<script type="application/json" id="<name>-data">…</script>` so the dated HTML works from `file://` and as a Slack attachment.
- Query the **web dbt mart** `cashdoc-5f28d.dbt_cashdoc_503924473_original_mart.cashdoc`, run with `bq query --project_id=cashdoc-5f28d`; pipe SQL via stdin (a leading `--` comment is read as a flag).

> 한글: 폴더에 HTML·탐색/본 쿼리·조회 스크립트·README를 둔다. 데이터는 HTML 안 JSON 블록에 넣어 파일 하나로 공유되게 한다. 웹 데이터는 dbt 웹 마트에서, SQL은 stdin으로 넘긴다.

## Numbers the pipeline can produce
- Grain is **one value per day per tag** (`daily_metrics`). Show daily series and period averages of daily values.
- Never show period-distinct users ("기간 순방문자 205명"); Evidence can't reproduce it. Use daily users and say "일평균".
- Ratios are **sum ÷ sum** over the period, never the mean of daily ratios.
- Users never add across pages/tags; if a total is needed, compute a deduplicated "all" value the producer will also store.

> 한글: 저장 단위는 날짜×태그 하루 값이다. 기간 고유 사용자 수처럼 Evidence가 재현 못 하는 숫자는 쓰지 않는다. 비율은 합계÷합계, 사용자는 지면끼리 더하지 않는다.

## Page shape (copy Evidence, don't invent)
- App chrome like production Evidence: sticky header (evidence logo → `https://main.evidence.smartdoctor.systems/`), **left sidebar** with the real dashboards grouped as in production (build the list from `evidence/pages/<group>/*.md` frontmatter `title` + `sidebar_position`, group title and group order from `<group>/index.md` `title`/`sidebar_position`; on ties copy the order shown on the production sidebar), the proposed page inserted at its planned spot, highlighted and tagged "제안" (other items open the production page in a new tab), breadcrumb `홈 › <그룹> › <페이지>`, hamburger toggle under ~900px.
- Layout: intro panel (what it answers + scope list) → filter bar (기간 presets, 일간/주간, dimension dropdowns, **all functional**) → numbered sections ①②… each with a one-line sub → KPI strip → charts/tables.
- Colors: Evidence `components/chartPalette.js` tokens only (`palette`, `lineAccents`, `accent.emphasis`); pick series colors ≥ OKLab ΔE 10 apart. The pastel `palette` alone can't separate 4+ series, so mix in the darker `lineAccents`. Status/ratio warnings in amber text.
- Every widget gets a "지표 설명" with the **planned metric name + tags + calculation** (e.g. `cashdoc.coupon.click.users.count {section,name}`, "클릭 사용자 ÷ 진입 사용자"). Keep a METRICS dictionary in the page; it becomes `metricDescriptions.js`.
- Not-yet-tracked metrics: draw with sample data, a visible "목" tag on the section and widget, and the event that will feed it.
- Labels are user-facing words, never raw keys (`phr_empty` → "연동 안 함 · 내역 없음"). Descriptions are one short sentence in the existing Evidence tone; drop obvious "how to read" lines.

> 한글: 운영 Evidence 겉모양(상단 헤더, 그룹별 대시보드 사이드바에 새 페이지를 '제안' 태그로 끼워 넣기, 브레드크럼, 모바일 햄버거)까지 똑같이 만든다. 본문은 Evidence 구성을 따른다(소개→동작하는 필터→번호 섹션→KPI→차트). 색은 Evidence 팔레트만, 위젯마다 예정 지표명·태그·계산식을 적는다. 미수집 지표는 예시 데이터 + '목' 표시 + 필요한 이벤트. 라벨은 사용자 언어, 설명은 한 문장.

## Before showing the lead
1. Open it in a browser (serve the folder locally) and screenshot every section: horizontal bar labels not clipped, legends readable, empty states, filters change the charts.
2. Ask one subagent for a 불편/부족/과한 critique of the page; fix what's real.
3. Save the file, publish an Artifact for viewing, and send the lead: file path/link + **1–2 lines per section** + which parts are 목 + open questions.
4. Iterate on feedback in the same file; the approved version is the spec. Keep it; the Evidence page is later diffed against it.

> 한글: 브라우저로 열어 섹션별 스크린샷을 보고(라벨 잘림, 범례, 빈 상태, 필터 동작), 다른 에이전트에게 불편·부족·과한 점을 받아 고친다. 파일 저장 + 아티팩트 링크 + 섹션별 1~2줄 요약 + 목 부분·미결 사항을 함께 보낸다. 승인본은 Evidence 대조 기준이니 보관한다.

## Common mistakes
| Mistake | Fix |
|---|---|
| Numbers typed into the HTML, queries not saved | `sql/` + fetch script + embedded JSON |
| Filters that only look like filters | Wire them or remove them |
| Period-distinct users, averaged ratios | Daily values, sum ÷ sum |
| Invented palette | Evidence `chartPalette.js` tokens |
| Bare page without the Evidence sidebar/header | Copy the production chrome so the lead sees where the page will live |
| "Done" without opening it | Screenshot every section first |
