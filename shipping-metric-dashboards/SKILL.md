---
name: shipping-metric-dashboards
description: Use when a lead asks for a usage/performance dashboard of a Cashdoc web (astro) page or feature, when work spans BigQuery exploration, an HTML chart mockup, new GA events, a DE mart key request, a Prefect daily_metrics producer and an Evidence page, or when an Evidence page must match an approved mockup.
---

# Shipping Metric Dashboards (BigQuery → mockup → GA → Prefect → Evidence)

## Overview
A dashboard ships through seven gated stages owned by different people. Most failures are not in the code but at the seams: the page silently drifts from the approved mockup, data arrives later than the page, or production never actually picks up the build. Each stage below has an exit check; do not start the next stage until it passes.

> 한글: 대시보드는 담당자가 다른 7단계를 거친다. 실패는 대부분 단계 사이 이음새에서 난다(목업과 화면이 몰래 달라짐, 데이터가 화면보다 늦게 옴, 운영이 새 빌드를 안 받음). 단계마다 통과 조건을 확인하고 다음으로 넘어간다.

## Stages and exit checks

| # | Stage | Produce | Exit check |
|---|---|---|---|
| 1 | BigQuery | Queries on the **web dbt mart** `cashdoc-5f28d.dbt_cashdoc_503924473_original_mart.cashdoc` (not the app mart `cashwalk-971ff…`). Same path regex/login rule/bot filter the producer will use | Numbers reproduce on 2 dates |
| 2 | HTML mockup | **REQUIRED SUB-SKILL:** Use drafting-dashboard-mockups (reproducible folder, pipeline-producible numbers, planned metric names, visible "목" for untracked metrics) | Lead approves it. Keep the approved file; it is the spec for stage 6 |
| 3 | GA events | Event spec as "button → expected event" doc, frontend PR, test-server check with GA debugger | Events visible in BigQuery intraday after prod deploy. **Record the exact prod deploy time** |
| 4 | DE mart key | Web dbt mart loads every new `event_label` automatically; request only **new parameter keys** (`ep_<key>`) via the 오리지널 마트 Key workflow | Key columns present in the mart |
| 5 | Prefect producer | Flow + SQL + registry entry; verify with `build_rows(as_of)` only (no production writes) | PR merged, then backfill run (see Release order) |
| 6 | Evidence page | Sources with `__pending__` sentinel, page, catalog/description/settlement entries, `npm run policy:generate && npm run check && npm run build` | **Mockup diff check** passes (below) |
| 7 | Production | Merge, wait for the live build, verify real data | Checklist under "Production verify" passes |

> 한글: 웹 GA는 dbt 웹 마트(`cashdoc-5f28d…`)에서 본다. 목업은 Evidence 모양으로, 미수집 지표는 '목' 표시. GA는 상용 배포 시각을 기록한다(그날은 반나절치). DE에는 새 파라미터 키만 요청(라벨은 자동 적재). Prefect는 `build_rows`로만 검증한다.

## Mockup diff check (before opening the Evidence PR)
Open the mockup and the local Evidence page side by side and list, per section: order, title, widgets, filters/defaults, copy, extra/missing sections. Any difference you introduced (e.g. Evidence component limits) is reported to the user **before** the PR with the reason, never discovered later by the reviewer.

> 한글: Evidence PR 전에 목업과 섹션 순서·제목·위젯·필터 기본값·문구를 나란히 대조하고, 일부러 바꾼 점은 이유와 함께 PR 전에 사용자에게 먼저 알린다. 리뷰어나 사용자가 나중에 발견하게 두지 않는다.

## Previewing Evidence without a DB tunnel
- Before backfill: write mock Parquet into `.evidence/template/static/data/openapi/<source>/<any-hash>/<source>.parquet` and add it to `.evidence/template/static/data/manifest.json` `renderedFiles.openapi`. Generate with `@duckdb/node-api` from a script kept in the scratchpad.
- After backfill on production: mirror real files from `https://main.evidence.smartdoctor.systems/data/manifest.json` into the same place.
- `.evidence/` and `build/` are git-ignored; still run `git status` before every commit and delete mock files/manifest entries before the PR. `npm run build` stops a running `evidence dev`.

> 한글: 데이터가 없을 땐 목 Parquet을, backfill 후엔 운영 Parquet을 `.evidence/` 아래에 넣고 manifest에 등록해 로컬에서 본다. git이 무시하는 폴더지만 커밋 전 `git status`로 확인하고 PR 전에 목 파일을 지운다.

## Release order
1. Merge the Prefect PR (human click) → wait for `build-and-deploy-prefect` → confirm the deployment version equals the merge commit in the Prefect UI.
2. Backfill: deployment `all-to-evidence-backfill-flow`, custom run with `start_date` = first data date, `end_date` = KST today − 3, `only=["cashdoc.<registry name>"]` (domain-prefixed, e.g. `cashdoc.mypage` for the `("mypage", …)` entry in `flows/evidence/cashdoc/registry.py`; a bare `"mypage"` is rejected) (URL-prefill: `…/run?parameters=` + double-encoded JSON). Confirm every per-date subflow is green.
3. Merge the Evidence PR. The sentinel keeps the build green even if data is missing, but merging first ships an empty page.

> 한글: prefect 머지 → 배포 버전 확인 → backfill(`only`에는 `cashdoc.<이름>`) → evidence 머지 순서. 순서를 뒤집으면 빈 페이지가 먼저 나간다.

## Production verify (Evidence)
- `curl /healthz` shows the new build time; `/data/manifest.json` lists the new sources; open the route and read the console.
- Pods rebuild the whole site at startup (~5 min). If the site stays on the old build >15 min, open ArgoCD app `evidence`: a red pod with "Startup probe failed … connection refused" then "Killing" means the build outlived the probe and restarts (usually passes on retry); "readiness gate target-health.elbv2… does not exist" means waiting on ALB registration. Do not press Sync/Delete; escalate to the Evidence owner if stuck.

> 한글: 워크플로 성공만으로 '배포 완료'라 하지 않는다. healthz 빌드 시각·manifest·실제 화면을 본다. 15분 넘게 옛 빌드면 ArgoCD에서 파드 EVENTS/LOGS만 보고(startup probe 초과는 재시도로 보통 통과, readiness gate는 ALB 등록 대기), Sync/Delete는 누르지 않는다.

## Data gotchas that change numbers
- GA values settle late; producers load KST today − 3 and the page date picker stops there. Say so on the page.
- The GA deploy date is a **partial day** and earlier dates are "not measured", not zero: start event charts at the first event date and annotate it.
- Unique users never add across tags or days: store a deduplicated `all` row (`GROUPING SETS`) and read it for totals.
- Producers fold empty/unknown tag values into `unknown`; every chart that buckets tags needs an "알 수 없음" bucket or totals won't match KPIs.
- A ratio KPI over sparse event rows needs explicit zero-fill (`coalesce(x, case when denom is not null then 0 end)`), otherwise days with no numerator drop out of the denominator.
- Funnel steps must be subsets of the previous step; if users can enter mid-funnel, start the funnel there. Every note must match the SQL.

> 한글: D-3 적재, GA 배포일은 반나절치·그 전은 0이 아니라 미측정, 순사용자는 `all` 행으로만 합계, `unknown`은 '알 수 없음'으로 남기기, 희소 이벤트 비율은 0 채우기, 퍼널은 앞 단계의 부분집합이어야 하고 설명 문구는 SQL과 맞아야 한다.

## Evidence UI gotchas
- Renaming or reusing an input `name` breaks old links: a stale `?page=home` silently becomes a different filter. Give new filters new names.
- Repo-patched `Dropdown`: clicking an option label selects only that option; pass `labelSoloSelect={false}` for multi-pick lists. Options sort by label unless `order` is passed.
- `DataTable` title-cases column ids ("PV" → "Pv"): pass `title=`. Sparkline tooltips need `name`.
- Pastel palette blues (palette 0/3/5/8) are near-identical; pick series colors by OKLab ΔE ≥ 10 and fix colors per entity, not per rank.

> 한글: 필터 이름을 재사용하면 옛 링크가 다른 필터로 읽힌다. 다중 선택은 `labelSoloSelect={false}`, 정렬은 `order`. 표 헤더는 `title=`, 스파크라인은 `name`. 색은 OKLab ΔE 10 이상으로 고르고 대상별로 고정한다.

## Common mistakes
| Mistake | Fix |
|---|---|
| Rebuilding the page "the Evidence way" and silently dropping mockup sections/filters | Mockup diff check; ask before deviating |
| Showing an empty Evidence page because data comes later | Mock/mirrored Parquet locally; backfill before merge |
| Reporting "deployed" after the workflow succeeds | Verify healthz build time + route content |
| Asking DE to register every new event | Only new parameter keys |

> 한글: 흔한 실수 — 목업 섹션을 몰래 빼기, 데이터 없는 빈 페이지 내보내기, 워크플로 성공만 보고 배포 완료라 하기, DE에 이벤트마다 등록 요청하기.
