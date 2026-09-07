import os
import json
import markdown
import requests
import time
from datetime import date, timedelta

# Personal imports
from email_handler import send_email
from article_vetter import vet_articles
from data_cleaner import get_human_legible_txt
from vibe_checker import get_gossip_sentiment
from ai_orchestrator import AIOrchestrator
from search_orchestrator import SearchOrchestrator

search = SearchOrchestrator()
ai = AIOrchestrator()

# Initial search

response = search.search("OpenAI OR Anthropic OR Google DeepMind OR Meta AI OR Mistral OR xAI OR AI OR Artificial Intelligence", topic="news", time_range="day", max_results="5")

def viewResponse(title, url, content, score, published_date, formatter=""):
    print(formatter + "Title\n" + formatter + title + "\n")
    print(formatter + "url: " + url + "\n")
    print(formatter + "Content\n" + formatter + content + "\n")
    print(formatter + "Relevance: " + score + "\n")
    print(formatter + "Published: " + published_date + "\n")
    print(formatter + "---------------------------------------")

# # Vet Article Sources to obtain corroborate and consequential sources for the newsletter.
vetted_articles = vet_articles(response, search, ai)

vetted_article_titles = [d["title"] for d in vetted_articles]
vetted_article_urls = [d["url"] for d in vetted_articles]
        
print("*************************************************************************************************")
print("VALIDATED RESULTS:")
signal_sources_txt = []
for vetted_article in vetted_articles:
    viewResponse(vetted_article["title"], vetted_article["url"], vetted_article["content"], str(vetted_article["score"]), str(vetted_article["published_date"]))
    extract_text = search.extract(vetted_article["url"])
    signal_sources_txt.append(extract_text)

# Data cleaning
human_readable_source_txt = get_human_legible_txt(signal_sources_txt)

# Summarize each source
source_summaries = []
for source in human_readable_source_txt:
    prompt = """Summarize the following source in 120–150 words.""" + source

    summary_result = ai.generate(prompt, "open_router")
    print(summary_result)
    source_summaries.append(summary_result)
    
print()

# --------------------------------------------------------------------------------------------------
# RETRIEVE GOSSIP - X and Reddit

unfiltered_gossip = get_gossip_sentiment(vetted_article_titles, search, ai)

print("*************************************************************************************************")
print("VALIDATED RESULTS:")
for key in unfiltered_gossip:
    print(key + ": " + unfiltered_gossip[key]["gossip_sentiment"])

# --------------------------------------------------------------------------------------------------
# GitHub Repo of the Day

days_ago = 7
target_date = date.today() - timedelta(days=days_ago)
search_date = str(target_date.isoformat())
github_query = "https://api.github.com/search/repositories?q=created:>"+search_date+"&sort=stars&order=desc&topic=ai"
top_repo = requests.get(github_query)

github_history_file = "github_repo_history.json"
with open(github_history_file, 'r') as file:
    github_history = json.load(file)

repo = top_repo.json()["items"][0]
counter = 1
while(repo.get("html_url") in github_history["urls"] and counter <= 10):
    repo = top_repo.json()["items"][counter]
    counter += 1

github_history["urls"].pop(0)
github_history["urls"].append(repo.get("html_url"))

with open(github_history_file, "w", encoding="utf-8") as file:
    json.dump(github_history, file, indent=4)

github_repo_of_the_day = {
    "name": repo.get("name"),
    "url": repo.get("html_url"),
    "description": repo.get("description"),
    "homepage": repo.get("homepage"),
    "stars": repo.get("stargazers_count"),
    "language": repo.get("language")
}

print("*************************************************************************************************")
print("GitHub Repo Results:")
print(github_repo_of_the_day)
print()

# --------------------------------------------------------------------------------------------------
# Newsletter Generation!!!
# Combine all the info to create the newsletter.
# Prompt = Article Summaries + Gossip Sentiments + GitHub Repo of the Day

news_info = ""
for i in range(0, len(vetted_article_titles)):
    news_info += f"""
    Article Title: {vetted_article_titles[i]}
    Article URL: {vetted_article_urls[i]}
    Article Info:
    {source_summaries[i]}\n\n"""

if news_info == "":
    news_info = "No vetted or consequential news today. Have a good day!"

ultimate_prompt = f"""
Create a markdown formatted newsletter with a reading time of about four minutes.
The audience of this newsletter are smart, curious, non-technical business owners.
The newsletter should contain the following sections with relevant information:

The Big Story
The one thing that matters most today, and why.

Frontier Watch
A sentence on how what each source is about and how it relates to at least two of the following:
time saved, costs reduced, or revenue unlocked. Be specific when talking about what parts specifically 
relate to the time saved, costs reduced, or revenue unlocked. Include hyperlinks to the relevant article
the content was sourced from. Include any other relevant information from these sources you deem worth
knowing.
Sources - If there are no sources provided, state so:
{news_info}

The Street Says
Sentiment, gossip, and hot takes from X and Reddit.
X - If there is no gossip provided, state so:
{unfiltered_gossip["x"]["gossip_sentiment"]}
Reddit - If there is no gossip provided, state so:
{unfiltered_gossip["reddit"]["gossip_sentiment"]}

Repo of the Day
Information on one GitHub project worth knowing about. Use the following information provided for the
GitHub repo of the day.
{str(github_repo_of_the_day)}

Two Steps Ahead
A short forward-looking take: what today's news hints at for tomorrow."""

newsletter_message = ai.generate(ultimate_prompt, "nvidia", "advanced")

message = markdown.markdown(newsletter_message)

archival_file_name = str(date.today().isoformat()) + "_AI_Newsletter.html"
file_location = os.path.join("newsletter_archive", archival_file_name)
with open(file_location, "w", encoding="utf-8") as file:
    file.write(message)

# --------------------------------------------------------------------------------------------------
# SEND EMAIL

print("****************************************************************************")
print("SENDING")
print(message)

send_email(message)