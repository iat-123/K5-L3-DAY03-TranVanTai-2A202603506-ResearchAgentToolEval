# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: TranVanTai_2A202603506
- Members: Trần Văn Tài (2A202603506); Nguyễn Thị Hải Yến (2A202603567); Kiều Văn Thắng (2A202603424); Nguyễn Công Tĩnh (2A202603373); Hồ Xuân Vũ (2A202603406)
- Provider/model: OpenRouter / `openai/gpt-4o-mini`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent hỗ trợ tìm kiếm thông tin trên web và X/Twitter, đọc URL, tra cứu policy nội bộ hoặc paper arXiv, rồi lọc/loại trùng, so sánh nguồn và định dạng kết quả thành digest. Có thể lưu digest Markdown vào thư mục báo cáo cục bộ sau khi xác nhận. Tool gửi Telegram có sẵn nhưng giao diện demo hiện chặn gửi thật.

**Link dùng thử (deploy):**

Cloudflare Tunnel (tạm thời, chỉ hoạt động khi tunnel đang chạy): https://sensitivity-miscellaneous-binding-invoice.trycloudflare.com

## A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi người dùng khi thiếu thông tin hoặc cần xác nhận | không |
| timeline | Lấy bài đăng gần đây của một tài khoản X/Twitter | không |
| social_search | Tìm bài đăng X/Twitter theo chủ đề | không |
| lookup | Tìm thông tin trên web, gồm tin tức | không |
| fetch | Đọc nội dung từ URL cụ thể | không |
| format | Định dạng các kết quả đã có thành digest Markdown | không |
| deduplicate | Loại kết quả trùng theo URL hoặc tiêu đề | có |
| filter_results | Lọc kết quả đã thu thập theo từ khóa, domain hoặc giới hạn | có |
| compare_sources | Tạo bảng so sánh từ các trường có sẵn của nhiều nguồn | có |
| export_digest | Lưu digest Markdown vào thư mục reports sau khi xác nhận | có |
| send | Gửi nội dung lên Telegram sau khi được xác nhận; bị tắt trong UI demo | không |
| policy | Tìm kiếm tài liệu policy nội bộ | không |
| papers | Tìm paper trên arXiv | không |
| paper_text | Tải PDF arXiv và trích xuất văn bản cục bộ | không |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1. “Tìm tin tức AI hôm nay trên web.”
2. “Tìm các bài đăng phổ biến nhất về OpenAI trên X.”
3. “Tóm tắt trang này: https://example.com/research”
4. “Tìm các paper arXiv về transformer và ưu tiên bài mới cập nhật.”
5. “Loại kết quả trùng lặp trong danh sách nghiên cứu này.”

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Metrics are shown as case accuracy / tool routing / argument / multiturn accuracy. v5 distinguishes confirmation to prepare a draft from explicit approval to send its exact contents.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | Baseline | Baseline measurement before optimization. | N/A | 0.65 / 0.75 / 0.65 / 1.00 | `runs/v0_B_base_openrouter_20261110T112639908658.json` |
| v1 | `system_prompt.md` | Explicitly asking instead of guessing when essential information is missing should improve clarification behavior. | 0.65 / 0.75 / 0.65 / 1.00 | 0.75 / 0.90 / 0.75 / 0.8333 | `runs/v1_B_base_openrouter_20261110T113403688786.json` |
| v2 | `system_prompt.md`, `tools.yaml` | Specifying `clarify.response_type="text"` and providing clearer tool descriptions/argument conventions should improve missing-information handling and argument accuracy. | 0.75 / 0.90 / 0.75 / 0.8333 | 0.90 / 0.90 / 0.90 / 0.8333 | `runs/v2_B_base_openrouter_20261110T122959838115.json` |
| v3 | `system_prompt.md` | Requiring explicit yes/no confirmation before a send action should improve confirmation behavior. | 0.90 / 0.90 / 0.90 / 0.8333 | 0.95 / 1.00 / 0.95 / 1.00 | `runs/v3_B_base_openrouter_20261110T123649089281.json` |
| v4 | `system_prompt.md`, `tools.yaml`, three local tools | Add filtering, source comparison, and confirmed Markdown export; new group cases were added. | 0.95 / 1.00 / 0.95 / 1.00 | Base: 0.95 / 1.00 / 0.95 / 1.00; group: 1.00 / 1.00 / 1.00 / 1.00 | `runs/v4_B_base_openrouter_20261110T142615936871.json`; `runs/v4_B_group_openrouter_20261110T142442519939.json` |
| v5 | `system_prompt.md`, `tools.yaml` | Separate yes/no confirmation to prepare a draft from approval to send the exact content. | 0.95 / 1.00 / 0.95 / 1.00 | Base: 1.00 / 1.00 / 1.00 / 1.00; group: 1.00 / 1.00 / 1.00 / 1.00 | `runs/v5_B_base_openrouter_20261110T151909368918.json`; `runs/v5_B_group_openrouter_20261110T151949560920.json` |

## B2. Failure Analysis

Failures below are historical failures from the fixed base runs. v5 resolves the R12 eval mismatch while retaining a separate exact-content approval requirement before any send.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing (v0) | wrong_tool / wrong_arg_value | `lookup(query="AI news", topic="news", timeframe="day")` | Query included the word “news”; expected query `AI`. | Added argument conventions for web news search; passed in v1+. |
| R08_out_of_scope (v0) | out_of_scope | `send(text="<integral answer>")` | Called a tool for an out-of-scope math question instead of answering/refusing without tools. | Remove the “always use one tool” instruction; retain as a prompt improvement opportunity. |
| R10_missing_handle (v0) | missing_info | `timeline(screenname="sama")` | Guessed an account instead of asking the user. | Ask with `clarify`; v1+ routes to clarify. |
| R11_missing_url (v0) | missing_info | `fetch(url="https://example.com/article")` | Guessed a URL instead of asking for the article link. | Ask with `clarify`; v1+ routes to clarify. |
| R12_confirm_before_send (v0) | wrong_boundary | `send(text="...")` | Attempted the send action without first asking for confirmation. This is a confirmation-flow failure, not a Telegram connectivity failure. | Require explicit confirmation before send. v3 asks, but uses the wrong response type. |
| R13_parallel_web_and_tweets (v0) | wrong_tool / wrong_arg_value | `lookup(query="AI news", timeframe="day")`; `social_search(query="AI")` | Lookup omitted `topic="news"` and used an imprecise query. | Clarify query/topic conventions in tool descriptions; later runs improved this case. |
| R14_out_of_scope_coding (v0) | out_of_scope | `send(text="<Fibonacci code>")` | Called a tool for an out-of-scope coding request. | Remove the “always use one tool” instruction; retain as a prompt improvement opportunity. |
| M06_switch_tool (v1–v2) | wrong_tool | `social_search(query="OpenAI", ...)` | Used social search where the case expected web lookup. | Add a clearer web-vs-social routing rule; v3 passed this case. |
| R12_confirm_before_send (v3–v4) | wrong_boundary | `clarify(response_type="text")` | Correctly asked for missing bulletin content, but the fixed eval expected a yes/no response. This is not a Telegram connectivity failure. | v5 uses yes/no only to confirm intent to prepare a draft; it explicitly states this is not approval to send. Before sending, the exact content still requires a separate yes/no approval. R12 passes in v5. |

## B3. Team Eval Cases

Latest run: `runs/v5_B_group_openrouter_20261110T151949560920.json` — 13/13 passed; case accuracy 1.00, tool routing 1.00, argument accuracy 1.00, multiturn accuracy 1.00.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_deduplicate_research_items | Route duplicate research items to deduplication | `deduplicate` | PASS |
| G02_social_search_topic | Search X posts by topic, not by account | `social_search(query="GPT-5")` | PASS |
| G03_web_news_today | Route today's AI news to web news search | `lookup(query="AI", topic="news", timeframe="day")` | PASS |
| G04_fetch_given_url | Read a URL provided by the user | `fetch(url="https://example.com/research")` | PASS |
| G05_clarify_missing_article_url | Ask for a missing article URL instead of guessing | `clarify(response_type="text")` | PASS |
| G06_multiturn_timeline_account | Carry account and requested count through multiple turns | `timeline(screenname="elonmusk", limit=5)` | PASS |
| G07_multiturn_social_search_top | Carry topic and switch sorting to popular posts | `social_search(query="OpenAI", search_type="Top")` | PASS |
| G08_multiturn_lookup_timeframe | Update topic and preserve today's news timeframe | `lookup(query="robotics", topic="news", timeframe="day")` | PASS |
| G09_multiturn_fetch_url | Use URL supplied in a later turn | `fetch(url="https://example.com/ai-report")` | PASS |
| G10_multiturn_arxiv_papers | Carry arXiv topic and sort by recently updated | `papers(query="transformer", sort_by="lastUpdatedDate")` | PASS |
| G11_filter_research_results | Filter collected results by criteria | `filter_results` | PASS |
| G12_compare_research_sources | Compare two existing research results | `compare_sources` | PASS |
| G13_confirmed_export_digest | Require confirmation before local file write | `export_digest(confirmed=true)` | PASS |

## B4. Live Chat Evidence

Source: `transcripts/v0_openrouter_20261110T111219174230.transcript.json` (three answered turns; artifact hash matches the v0 baseline).

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | “hello” | none | v0, OpenRouter `openai/gpt-4o-mini` | Answered greeting |
| 2 | “Ban co the lam gi” | none | v0, same transcript | Described agent capabilities |
| 3 | “hien tai nhiet do ngoai troi o ha noi la bn” | `lookup(query="current temperature in Hanoi", topic="general")` | v0, same transcript | Answered with sources; source quality should be reviewed because one cited source was a Facebook post |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `tests/test_tools_todo.py`; `app/app.py` | Offline mock verifies a confirmed send request is formed; UI blocks Telegram sending | No live Telegram connectivity was tested; UI does not send messages |
| arXiv/company policy | `tools/papers/`; `tools/paper_text/`; `tools/policy/`; group eval G10; policy unit tests | arXiv search route passed group eval; policy filtering and untrusted-text handling are unit-tested | arXiv is rate-limited and paper text writes files locally; retrieved policy text is untrusted reference data |
| UI | `app/app.py`; Cloudflare Tunnel | Streamlit UI started locally and passed an AppTest smoke check; temporary public tunnel responded successfully | Link is temporary and only works while both Streamlit and cloudflared are running; Telegram action is disabled in the demo UI |
| Tool unit tests (`tests/`) | `python -m pytest -q` | 112 passed, 0 skipped; each of the three additional tools has four offline unit tests | HTTP calls are mocked; provider evals confirm model routing, not live API availability for unrelated external services |

Tool unit tests: `deduplicate`, `filter_results`, `compare_sources`, and `export_digest` are the four team-added tools; each has at least three unit tests. The export tool requires explicit confirmation, writes only under `starter_v0/reports/`, and never overwrites an existing file.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`? Rules for asking instead of guessing when essential information is missing, and for requesting explicit confirmation before send.
- Which fixes belonged in `tools.yaml`? Tool-selection boundaries and argument conventions such as handle format, `topic=news`, `timeframe`, `search_type`, and confirmation requirements.
- Which failure needed manual review instead of automatic grading? Source quality in the live transcript (for example, whether a Facebook post is adequate evidence for current weather) and whether a confirmation question clearly presents the exact content to be sent.
- What would you improve next? Make the send-confirmation flow ask for missing message content first and then ask yes/no confirmation; evaluate source quality, deploy the UI for a demo, and add more diverse group cases.

## B7. Small Local Model Challenge (bonus)

Not run in this project session. This is an optional challenge; no Ollama run artifacts are available, so the comparison tables below are intentionally left unfilled.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?
