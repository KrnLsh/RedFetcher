import praw
import os
import sys
import tiktoken
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By

CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = None
USER_AGENT = 'YOUR_USER_AGENT'

def get_reddit_instance():
    return praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )

def print_status(state):
    limit_str = str(state['limit']) if state['limit'] else "Unlimited"
    msg = f"[{state['thread_info']}] {state['status']} | Tokens: {state['tokens']} / {limit_str}"
    sys.stdout.write(f"\r{msg:<150}")
    sys.stdout.flush()

def write_and_count(text, file_handle, state, enc):
    if state['reached']:
        return

    tokens = len(enc.encode(text, disallowed_special=()))
    
    if state['limit'] is not None and (state['tokens'] + tokens) >= state['limit']:
        state['reached'] = True
        return 

    file_handle.write(text)
    state['tokens'] += tokens
    print_status(state)

def write_comments(comments, file_handle, level, state, enc):
    for comment in comments:
        if state['reached']:
            break
            
        indent = "    " * level
        author = comment.author.name if comment.author else "[deleted]"
        body = comment.body.replace('\n', f'\n{indent}  ').strip()
        
        text_to_write = f"{indent}-> [{author}]: {body}\n"
        write_and_count(text_to_write, file_handle, state, enc)
        
        if comment.replies:
            write_comments(comment.replies, file_handle, level + 1, state, enc)

def get_thread_urls_from_browser(query, scope):
    print(f"\n[Browser] Launching browser...")
    
    encoded_query = urllib.parse.quote(query)
    if scope.lower() == 'all':
        search_url = f"https://www.reddit.com/search/?q={encoded_query}&type=link"
    else:
        search_url = f"https://www.reddit.com/r/{scope}/search/?q={encoded_query}&restrict_sr=1&type=link"
        
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    
    try:
        print("\n[Browser] Opening Reddit login page...")
        driver.get("https://www.reddit.com/login")
        input("\n[ACTION REQUIRED] Please log in to Reddit in the opened browser window.\nOnce you are successfully logged in (or if you wish to skip), press Enter here to continue searching...")
        
        print(f"\n[Browser] Proceeding to search for '{query}'...")
        driver.get(search_url)
        time.sleep(3)
        
        urls = set()
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        target_limit = 500 
        
        print(f"[Browser] Gathering thread URLs from search. Please wait...")
        
        while len(urls) < target_limit:
            elements = driver.find_elements(By.TAG_NAME, 'a')
            for el in elements:
                try:
                    href = el.get_attribute('href')
                    if href and '/comments/' in href:
                        if href.startswith('/'):
                            href = f"https://www.reddit.com{href}"
                        
                        if 'reddit.com' in href:
                            clean_url = href.split('?')[0]
                            urls.add(clean_url)
                except Exception:
                    continue
            
            if len(urls) >= target_limit:
                break
                
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2.5)
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
    finally:
        driver.quit()
        
    urls_list = list(urls)[:target_limit]
    print(f"[Browser] Extracted {len(urls_list)} unique thread URL(s) from search.")
    return urls_list

def get_submissions(reddit, urls, state):
    for url in urls:
        state['status'] = 'Pinging API for URL...'
        print_status(state)
        try:
            yield reddit.submission(url=url)
        except Exception:
            continue

def main():
    print("=== Reddit Browser-Search -> API Scraper (Token Tracker Edition) ===")
    reddit = get_reddit_instance()
    
    try:
        enc = tiktoken.get_encoding("cl100k_base")
    except Exception as e:
        print(f"Error loading tokenizer: {e}")
        return

    step = 1
    query = input(f"{step}. Enter your search query OR a direct Reddit thread URL: ").strip()
    step += 1
    
    is_url = "reddit.com" in query or "redd.it" in query or query.startswith("http")
    
    if is_url:
        print("   -> Detected thread URL. Skipping browser search.")
        urls_to_scrape = [query]
        scope = "single_thread"
        safe_query = "Direct_URL"
    else:
        scope = input(f"{step}. Search entire Reddit ('all') or a specific subreddit? (Enter 'all' or sub name): ").strip()
        step += 1
        
        if scope.startswith('/r/'):
            scope = scope[3:]
        elif scope.startswith('r/'):
            scope = scope[2:]
            
        scope = scope.strip('/')
        
        if not scope or scope.lower() == 'search':
            scope = 'all'
        
        safe_query = "".join([c if c.isalnum() else "_" for c in query[:30]])
        
    token_input = input(f"{step}. Enter maximum token limit for the output txt file (Press Enter for unlimited): ").strip()
    step += 1
    max_tokens = int(token_input) if token_input.isdigit() else None

    if not is_url:
        urls_to_scrape = get_thread_urls_from_browser(query, scope)
        
        if not urls_to_scrape:
            print("No URLs found. Reddit might have blocked the search or there are no results.")
            return

    filename = f"Research_{safe_query}_{scope}.txt"
    
    state = {
        'tokens': 0, 
        'limit': max_tokens, 
        'reached': False,
        'thread_info': 'Init',
        'status': 'Starting API Scrape...'
    }

    print(f"\nStarting API extraction...\n")

    with open(filename, 'w', encoding='utf-8') as f:
        state['status'] = 'Writing headers'
        header_query = query if not is_url else f"URL: {query}"
        header = f"RESEARCH QUERY: {header_query}\nSOURCE: {'Thread' if is_url else 'r/'+scope}\n{'='*60}\n\n"
        write_and_count(header, f, state, enc)

        thread_count = 0
        limit_str = str(len(urls_to_scrape))

        for submission in get_submissions(reddit, urls_to_scrape, state):
            if state['reached']:
                break
                
            thread_count += 1
            
            safe_title = submission.title.replace('\n', ' ').replace('\r', '')
            if len(safe_title) > 40:
                safe_title = safe_title[:37] + "..."
                
            state['thread_info'] = f"Thread {thread_count}/{limit_str}: {safe_title}"
            state['status'] = 'Extracting post body'
            print_status(state)
            
            author = submission.author.name if submission.author else "[deleted]"
            
            thread_data = (
                f"THREAD TITLE: {submission.title}\n"
                f"THREAD AUTHOR: {author}\n"
                f"THREAD SCORE: {submission.score}\n"
                f"POST BODY:\n{submission.selftext}\n"
                f"{'-' * 30} COMMENTS {'-' * 30}\n"
            )
            write_and_count(thread_data, f, state, enc)
            if state['reached']: break
            
            state['status'] = 'Fetching nested comments...'
            print_status(state)
            
            try:
                submission.comments.replace_more(limit=None)
            except Exception:
                pass
            
            state['status'] = 'Extracting comments'
            print_status(state)
            
            write_comments(submission.comments, f, 0, state, enc)
            write_and_count(f"\n{'='*60}\n\n", f, state, enc)

    print("\n\n" + "="*40)
    print("EXTRACTION COMPLETE")
    print("="*40)
    
    if state['reached']:
        print(f"STOPPED: Reached your token limit of {max_tokens}.")
        
    if thread_count == 0:
        print("No valid threads scraped.")
        os.remove(filename)
    else:
        print(f"Total Unique Threads Scraped: {thread_count}")
        print(f"Total Tokens Extracted: {state['tokens']}")
        print(f"Data saved to: {os.path.abspath(filename)}")

if __name__ == "__main__":
    main()