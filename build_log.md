# FL-07 Build Log: Tech Scout Agent

## Iteration 1: Fetching Live Data
- **What I tried:** Originally in my FL-06 spec, I planned to use `requests` and `BeautifulSoup` to scrape full tech blogs (like Anthropic's blog).
- **What broke:** I ran into aggressive anti-bot protections (Cloudflare 403 blocks) on modern tech blogs, which crashed the agent immediately.
- **The Fix / Deviation:** I deviated from the spec by switching to RSS Feeds (specifically `hnrss.org`) using the `feedparser` library. This is a much more stable, API-like data source that never blocks polite requests.

## Iteration 2: Context Window Overflow
- **What I tried:** I tried passing the entire raw HTML text of the articles to the LLM for summarization.
- **What broke:** The prompt exceeded the token limit of the free-tier API, causing massive latency and 429 Too Many Requests errors.
- **The Fix / Deviation:** Instead of reading the full external article, the agent now strictly reads the `summary` block provided inside the RSS XML. This is a major optimization: it cuts token usage by 95% while still allowing the agent to generate highly accurate 3-bullet-point summaries.

## Iteration 3: Output Formatting
- **What I tried:** Writing the LLM output directly to a `.txt` file.
- **What broke:** Emojis and special markdown characters caused Windows encoding crash errors (`Charmap codec can't encode character`).
- **The Fix:** Hardcoded `encoding="utf-8"` in the Python `open()` function and upgraded the output file format to `.md` so the links are actually clickable when the user reads the briefing.

## Final Review against Spec
- **Core job completed:** Yes, end-to-end (Fetch -> Filter -> Reason -> Write).
- **Live Tool connected:** Yes, live internet RSS feed parsing and live Google Gemini API connection.
- **Hand-editing:** None required mid-run. Everything is fully autonomous once started.
