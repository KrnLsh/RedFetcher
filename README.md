# RedFetch

A lightweight, no-API-key-required Python tool designed to scrape Reddit discussions and format them into clean, nested text files. RedFetch is purpose-built to extract data for Large Language Models (LLMs) like ChatGPT, Claude, or Gemini, making it incredibly easy to summarize hours of product research, sentiment analysis, and community discussions in minutes.

## Features

* **No API Key Required:** Bypasses Reddit's developer API restrictions by leveraging public `.json` endpoints, meaning it works immediately out of the box.
* **Auto-Variation Search Engine:** Automatically maximizes your results by generating multiple search queries from your input. It strips fluff words, converts numerical values (e.g., `5000` to `5k`), removes prepositions, and runs sequential searches in the background to cast the widest net possible.
* **Built-in Deduplication:** Even when utilizing multiple search variations, the script tracks unique Post IDs to ensure you never get duplicate threads in your final text file.
* **Recursive Comment Extraction:** Does not just grab top-level comments. It recursively digs through the entire conversation tree, properly indenting nested replies so AI models can understand the context of the conversation.
* **Two-Phase Extraction & Dynamic UI:** Silently gathers unique posts in the background first, then utilizes a clean, single-line updating terminal UI that tracks the actual comment scraping progress without cluttering your console.
* **Customizable Search Parameters:** Allows users to define the target subreddit, search topic, post extraction limit, and preferred sorting method (Relevance, Top, New, Hot, or Comment Count).
* **HTML Sanitization:** Automatically translates HTML artifacts (like `&gt;`) back into standard text and filters out deleted or removed comments.

## Prerequisites

* Python 3.6 or higher
* `requests` library

## Installation

1. Clone the repository to your local machine:
```bash
git clone https://github.com/yourusername/RedFetch.git
cd RedFetch
```

2. Install the required dependencies:
```bash
pip install requests
```

## Usage

Run the script from your terminal:

```bash
python RedFetch.py
```

You will be prompted to enter your search criteria interactively:

1. **Subreddit:** Enter the target community (e.g., `mkindia`, `buildapc`).
2. **Topic:** Enter what you want to research (e.g., `best keyboard under 5000`).
3. **Limit:** Set the maximum number of posts to scrape (defaults to 8 if left blank).
4. **Sorting Method:** Choose how the search results are prioritized. 

### Example Interaction

```text
Reddit Scraper
----------------------------------------
1. Enter the subreddit name : mkindia
2. Enter the topic you want to research : best keyboard under 5000
3. Enter the number of posts to scrape [Press Enter for default: 8]: 5

4. Select sorting method:
   [1] Relevance (Default)
   [2] Top
   [3] New
   [4] Hot
   [5] Comments
Enter number [1-5]: 1

Auto-generated search variations:
  1. best keyboard under 5000
  2. keyboard under 5000
  3. keyboard under 5k
  4. keyboard 5k

Searching r/mkindia for up to 5 unique threads...

Scraping Thread 5/5: What keyboard should i get for under 5000                      

SUCCESS! 5 unique threads saved to: best_keyboard_under_5000_Reddit_Data.txt
```

## Output Format

The script generates a neatly formatted `.txt` file in the same directory. The output is structured to easily pass into an AI prompt window. 

**Sample Output Structure:**
```text
--- REDDIT SCRAPE DATA ---
SUBREDDIT: r/mkindia
ORIGINAL TOPIC: best keyboard under 5000
SORTED BY: relevance
TOTAL THREADS SCRAPED: 5
============================================================

TITLE: What keyboard should i get for under 5000
ORIGINAL POST: Looking for some suggestions for a mechanical keyboard...
COMMENTS:
- Have you checked out the Aula F75?
    - I second this. The stock switches are amazing for the price.
        - Thanks! I will look into it.
- Keychron C1 is also a solid choice if you want something minimal.
```

## AI Use Case

RedFetch structures data specifically for AI ingestion. To summarize your research:
1. Run RedFetch to generate your `.txt` file.
2. Open the file, select all (`Ctrl+A`), and copy (`Ctrl+C`).
3. Paste the contents into your preferred LLM alongside a prompt such as:
   * *"Based on this Reddit data, give me a list of Pros and Cons."*
   * *"What are the most common issues users face with this product?"*
   * *"Summarize the overall community sentiment."*

## Disclaimer

This script is for educational and personal research purposes. Please ensure your usage complies with Reddit's Terms of Service regarding data scraping and automated access. The script includes artificial delays (`time.sleep`) to respect rate limits and prevent IP blocking.