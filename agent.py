import os
import time
from datetime import datetime
import feedparser
import google.generativeai as genai

# --- CONFIGURATION ---
# Using HackerNews RSS to get real live data without getting blocked by anti-bot protections
RSS_FEED_URL = "https://hnrss.org/frontpage" 
TARGET_KEYWORDS = ["backend", "api", "database", "python", "agent", "llm", "ai", "architecture", "server", "code"]
OUTPUT_FOLDER = "Daily_Briefings"

def setup_agent():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\n[!] ERROR: GEMINI_API_KEY environment variable is missing.")
        print("[!] Get a free API key here in 2 minutes: https://aistudio.google.com/app/apikey")
        print("[!] Run this in terminal before running the script: $env:GEMINI_API_KEY='your_key_here'\n")
        exit(1)
    
    genai.configure(api_key=api_key)
    # The triad: Model + Tools + System Instruction
    model = genai.GenerativeModel(
        'gemini-1.5-flash', 
        system_instruction="You are a strict, concise technical research assistant. Summarize tech articles into exactly 3 bullet points focusing on engineering impact. If an article is pure marketing fluff, just output 'Not highly technical.'"
    )
    return model

def fetch_and_filter_feed():
    print(f"[*] Tool Call: Fetching RSS Feed from {RSS_FEED_URL}...")
    feed = feedparser.parse(RSS_FEED_URL)
    relevant_entries = []
    
    for entry in feed.entries:
        title = entry.title.lower()
        # Heuristic Filtering (First pass before hitting the expensive/slow LLM)
        if any(keyword in title for keyword in TARGET_KEYWORDS):
            relevant_entries.append(entry)
            
        # Hard limit to top 3 relevant articles to keep run times low and context windows safe
        if len(relevant_entries) >= 3:
            break
            
    return relevant_entries

def generate_briefing(model, entries):
    if not entries:
        return "## No highly relevant backend/AI articles found today."
        
    briefing = f"# Tech Scout Daily Briefing - {datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    for i, entry in enumerate(entries):
        print(f"[*] Agent Action: Reasoning over article {i+1}: {entry.title}...")
        
        # We pass only the summary from the RSS feed to avoid token limits from full HTML scraping
        prompt = f"Title: {entry.title}\nSummary: {entry.get('summary', 'No summary available.')}\n\nPlease generate a 3-bullet technical summary."
        
        try:
            response = model.generate_content(prompt)
            summary = response.text.strip()
        except Exception as e:
            summary = f"Error generating summary: {e}"
            
        briefing += f"### [{entry.title}]({entry.link})\n"
        briefing += f"{summary}\n\n---\n"
        time.sleep(1) # Polite delay for API limits
        
    return briefing

def main():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    model = setup_agent()
    
    print("[*] Starting Tech Scout Agent...")
    relevant_articles = fetch_and_filter_feed()
    print(f"[*] Pre-filtering complete. Found {len(relevant_articles)} relevant articles to read.")
    
    briefing_content = generate_briefing(model, relevant_articles)
    
    filename = os.path.join(OUTPUT_FOLDER, f"Briefing_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.md")
    print(f"[*] Tool Call: Writing output to local file system...")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(briefing_content)
        
    print(f"[*] Agent task complete. Briefing saved to {filename}")

if __name__ == "__main__":
    main()
