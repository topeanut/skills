---
name: drafting-slack-posts
description: Use when the user asks for a Slack message, thread reply, announcement, or team update to paste into Slack, especially when they will copy the reply with /copy. Also use for "슬랙에 올릴 글", "스레드 답글", "공지 초안", "팀에 공유할 글".
---

# Drafting Slack Posts

## Overview

The user copies the whole reply with `/copy` and pastes it into Slack unchanged. So **the entire reply is the post**: plain text that reads correctly in Slack without any markdown rendering.

This overrides output-style extras (Explanatory "★ Insight" boxes, preambles, closing questions) for that reply only.

> 한글: 사용자는 응답 전체를 `/copy`로 복사해 Slack에 그대로 붙인다. 그래서 **응답 전체가 곧 게시글**이다. 마크다운 없이도 Slack에서 자연스럽게 읽히는 평문으로 쓰고, 이 응답에서만 출력 스타일의 부가 요소(Insight 박스, 앞 설명, 끝 질문)를 뺀다.

## The reply shape

The reply contains exactly these parts, in order, and nothing else:

1. Title line: plain text, optionally in square brackets — `[주간 대시보드 점검 이슈 대응]`
2. Blank line
3. Sections, each:
   - Heading line: `1. 후기 더보기 지표 누락`
   - Items: lines starting with `• ` (U+2022 + space)
   - Sub-items: lines starting with `  ◦ ` (two spaces, U+25E6, space)
4. One blank line between sections
5. Optional closing line addressed to the team (e.g. `의견 부탁드립니다 🙏`)

Emphasis comes from wording and order, not symbols. Write PR/issue refs, URLs, and @mentions as plain text (`PR #1831`, `CSD-9654`, `https://...`).

> 한글: 응답은 제목 줄 → 빈 줄 → 번호 섹션(`1. 제목`, 항목 `• `, 하위 항목 `  ◦ `) → 섹션 사이 빈 줄 → (선택) 팀에 건네는 마지막 한 줄, 이것만으로 이뤄진다. 강조는 기호가 아니라 문장과 순서로 한다. PR 번호·링크·멘션은 평문으로 쓴다.

## Example

```
[주간 대시보드 점검 이슈 대응]

1. 후기 더보기 지표 누락
• 원인: 9/27 배포(PR #1721)에서 더보기 버튼 GA가 빠짐
• 대응: 병원안내·후기 탭 더보기 버튼에 GA 다시 추가 (PR #1831)
  ◦ 9/28~배포 전 데이터는 복구 불가

2. 예약(비활성) 클릭 급증
• 캐시워크 사용자 1명의 초고속 연타(69ms 간격)
• 대응 방향 의견 부탁드립니다
  ◦ A. 집계를 사용자 수 기준으로 변경
  ◦ B. 웹뷰에서 연타 방지
```

(The fence above is only for showing the example in this file. The real reply has no fence.)

## Things the user needs to decide

Unknowns that change the post (channel, mention target, a date or number you are unsure of) get asked with AskUserQuestion **before** writing the post. After the post is written, the reply ends at the post's last line.

> 한글: 채널·멘션 대상·불확실한 날짜나 숫자처럼 글 내용을 바꾸는 미정 사항은 글을 쓰기 **전에** AskUserQuestion으로 묻는다. 글을 쓴 뒤 응답은 게시글 마지막 줄에서 끝난다.

## Quick check before sending

| Character / element in the reply | Replace with |
|---|---|
| `**x**`, `*x*`, `_x_`, `~x~` | plain `x` |
| `> ` quote lines | plain lines |
| `- ` / `* ` bullets | `• ` |
| `#` headings, `---`, tables, code fences | numbered heading lines, blank lines |
| `` `code` `` | plain text |
| Intro ("초안입니다"), Insight box, follow-up questions | remove; ask before drafting instead |

> 한글: 보내기 전 확인표 — `**`·`*`·`_`·`~` 강조, `> ` 인용, `- `/`* ` 글머리, `#` 제목·`---`·표·코드블록, 인라인 코드, 앞 설명·Insight·후속 질문이 남아 있으면 오른쪽 형태로 바꾼다.
