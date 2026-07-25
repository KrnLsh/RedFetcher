# RedFetch

A powerful Python research tool designed to search and scrape Reddit discussions, post bodies, and full nested comment trees into clean, token-counted text files.

By combining **PRAW** (Python Reddit API Wrapper) and **tiktoken** token budgeting, RedFetch lets you easily gather community feedback, sentiment, and product research pre-formatted specifically for Large Language Models (LLMs) like ChatGPT, Claude, and Gemini.

## Key Features

* **API-Based Search & Extraction:** Uses Reddit's API through **PRAW** for both search and deep extraction of post metadata and comments—no browser automation is involved.
* **Token-Budget Control (`tiktoken`):** Tracks precise OpenAI token counts (`cl100k_base`) in real-time as data is written. Set a token cap so your output file fits perfectly inside your LLM's context window.
* **Flexible Search & Direct URL Support:** Search across all of Reddit (`all`), restrict your search to a specific subreddit (`r/mkindia`), or paste a direct Reddit thread URL to scrape a single specific post.
* **No Browser Login:** Searches run through the Reddit API, so Chrome, Selenium, and Reddit account login prompts are not used.
* **Recursive Nested Comments:** Captures full comment hierarchy with structured indents and author tags (`-> [author]: comment body`) so AI models can understand conversation context.
* **Live Status Dashboard:** Terminal UI updates dynamically on a single line, displaying the current thread title, active operation, and live token count against your limit.

## Prerequisites

* Python 3.8 or higher
* Reddit API Credentials (for PRAW)

## Dependencies

Install the required Python packages:

```bash
pip install praw tiktoken
```

## Setup & Configuration

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/RedFetch.git
   cd RedFetch
   ```

2. **Add your Reddit API credentials:**
   Open `RedFetch.py` in your text editor and update the credentials at the top of the file:
   ```python
   CLIENT_ID = 'YOUR_CLIENT_ID'
   CLIENT_SECRET = 'YOUR_CLIENT_SECRET' # Or None if using script app without secret
   USER_AGENT = 'YOUR_USER_AGENT'
   ```

## Usage

Run the script from your terminal:

```bash
python RedFetch.py
```

Follow the interactive prompts:

1. **Query or URL:** Enter a search topic (e.g., `best mechanical keyboard`) **OR** paste a direct Reddit thread link.
2. **Scope:** Search across all of Reddit (`all`) or type a specific subreddit name (e.g., `mkindia`). *(Skipped if a direct URL is entered)*.
3. **Token Limit:** Enter the maximum token budget for your output file (e.g., `10000`). Press `Enter` for unlimited.

### Example Interaction

```text
=== Reddit API Search -> Scraper (Token Tracker Edition) ===
1. Enter your search query OR a direct Reddit thread URL: best mechanical keyboard under 5000
2. Search entire Reddit ('all') or a specific subreddit? (Enter 'all' or sub name): mkindia
3. Enter maximum token limit for the output txt file (Press Enter for unlimited): 5000

[API] Searching r/mkindia for 'best mechanical keyboard under 5000'...
[API] Found 42 unique thread URL(s).

Starting API extraction...

[Thread 1/42: What keyboard should I get for under 5... ] Extracting comments | Tokens: 3420 / 5000


========================================
EXTRACTION COMPLETE
========================================
STOPPED: Reached your token limit of 5000.
Total Unique Threads Scraped: 2
Total Tokens Extracted: 5012
Data saved to: /path/to/Research_best_mechanical_keyboard_under__mkindia.txt
```

## Output Format

The script generates a formatted `.txt` file ready to copy and paste into an AI prompt.

**Sample Output (`Research_query_subreddit.txt`):**

```text
RESEARCH QUERY: best mechanical keyboard under 5000
SOURCE: r/mkindia
============================================================

THREAD TITLE: What mechanical keyboard should I get for under 5000?
THREAD AUTHOR: tech_guy99
THREAD SCORE: 34
POST BODY:
Looking for suggestions for a solid budget mechanical keyboard for typing and gaming...
------------------------------ COMMENTS ------------------------------
-> [keyboard_fan]: Have you checked out the Aula F75?
    -> [tech_guy99]: I've seen it mentioned a lot, is build quality good?
        -> [keyboard_fan]: Yes, stock switches and gasket mount feel great for the price.
-> [budget_builder]: Keychron C1 is another great choice if you want hot-swappable switches.

============================================================
```

## Using Output with AI

1. Run **RedFetch** and set a token limit matching your AI model's context budget (e.g., `8000` tokens for ChatGPT/Claude).
2. Open the generated text file, copy its entire contents, and paste it into your AI prompt.
3. Example prompt ideas:
   * *"Analyze the sentiment across these Reddit discussions."*
   * *"Extract a list of recommended products along with user pros and cons."*
   * *"What are the most common complaints mentioned in these threads?"*

## Disclaimer

This tool is created for personal research and educational purposes. Ensure your usage complies with Reddit's Terms of Service and API Guidelines.
