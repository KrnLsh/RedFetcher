import requests
import time
import re
import html 

def generate_smart_query(user_topic):
    fluff_words = ["review", "reviews", "thoughts", "opinion", "opinions", "worth it", "vs", "good", "bad", "help", "question"]
    base_topic = user_topic.lower()
    for word in fluff_words:
        base_topic = re.sub(rf'\b{word}\b', '', base_topic).strip()
    
    base_topic = re.sub(' +', ' ', base_topic)

    if base_topic == user_topic.lower() or not base_topic:
        return f'"{user_topic}"'
    
    smart_query = f'"{user_topic}" OR "{base_topic}"'
    print(f"Smart Search Activated: {smart_query}")
    return smart_query

def extract_all_comments(children_list, indent_level=0):
    comments_text = ""
    indent = "    " * indent_level 
    
    for item in children_list:
        if item['kind'] == 't1' and 'body' in item['data']:
            raw_body = item['data']['body']
            clean_body = html.unescape(raw_body)
            clean_body = clean_body.replace('\n', ' ').strip()
            clean_body = re.sub(' +', ' ', clean_body)
            
            if clean_body not in ["[deleted]", "[removed]"]:
                comments_text += f"{indent}- {clean_body}\n"
            
            replies = item['data'].get('replies')
            if isinstance(replies, dict) and 'data' in replies and 'children' in replies['data']:
                comments_text += extract_all_comments(replies['data']['children'], indent_level + 1)
                
    return comments_text

def scrape_reddit_data(subreddit, user_topic, limit=8, sort_by="relevance"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
    }
    
    search_query = generate_smart_query(user_topic)
    print(f"\nSearching r/{subreddit} for the top {limit} threads sorted by {sort_by}...\n")
    
    search_url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {
        'q': search_query,
        'restrict_sr': 'on', 
        'sort': sort_by,
        'limit': limit
    }
    
    response = requests.get(search_url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Error fetching data: HTTP {response.status_code}")
        return
        
    search_data = response.json()
    posts = search_data['data']['children']
    
    if not posts:
        print("No posts found. Try a different topic or subreddit.")
        return

    output_text = f"--- REDDIT SCRAPE DATA ---\n"
    output_text += f"SUBREDDIT: r/{subreddit}\n"
    output_text += f"TOPIC: {user_topic}\n"
    output_text += f"SORTED BY: {sort_by}\n"
    output_text += ("="*60) + "\n\n"
    
    for index, post in enumerate(posts):
        post_data = post['data']
        title = post_data['title']
        permalink = post_data['permalink']
        
        display_text = f"Scraping Thread {index + 1}/{len(posts)}: {title}"
        print(f"\r{display_text[:75].ljust(75)}", end="", flush=True)
        
        output_text += f"TITLE: {title}\n"
        
        if post_data.get('selftext'):
            clean_body = html.unescape(post_data['selftext']).replace('\n', ' ').strip()
            if clean_body:
                output_text += f"ORIGINAL POST: {clean_body}\n"
                
        output_text += "COMMENTS:\n"
        
        comments_url = f"https://www.reddit.com{permalink}.json"
        comments_response = requests.get(comments_url, headers=headers)
        
        if comments_response.status_code == 200:
            comments_data = comments_response.json()
            root_comments = comments_data[1]['data']['children']
            output_text += extract_all_comments(root_comments, indent_level=0)
                    
        output_text += "\n" + ("="*60) + "\n\n"
        time.sleep(1.5) 

    clean_filename = re.sub(r'[^a-zA-Z0-9]', '_', user_topic)
    filename = f"{clean_filename}_Reddit_Data.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(output_text)
        
    print(f"\n\nAll raw data saved to: {filename}")


if __name__ == "__main__":
    print("Reddit Scraper")
    print("-" * 40)
    
    target_sub = input("1. Enter the subreddit name : ").replace("r/", "").strip()
    target_topic = input("2. Enter the topic you want to research : ").strip()
    
    limit_input = input("3. Enter the number of posts to scrape [Press Enter for default: 8]: ").strip()
    
    target_limit = 8 
    if limit_input:
        try:
            target_limit = int(limit_input)
            if target_limit <= 0:
                print("Number must be greater than 0. Using default: 8.")
                target_limit = 8
        except ValueError:
            print("Invalid number entered. Using default: 8.")
            target_limit = 8
            
    print("\n4. Select sorting method:")
    print("   [1] Relevance (Default)")
    print("   [2] Top")
    print("   [3] New")
    print("   [4] Hot")
    print("   [5] Comments")
    sort_input = input("Enter number [1-5]: ").strip()
    
    sort_options = {
        "1": "relevance",
        "2": "top",
        "3": "new",
        "4": "hot",
        "5": "comments"
    }
    
    target_sort = sort_options.get(sort_input, "relevance")
            
    scrape_reddit_data(subreddit=target_sub, user_topic=target_topic, limit=target_limit, sort_by=target_sort)