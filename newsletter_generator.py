import os
import json
from tavily import TavilyClient
import markdown
# from openrouter import OpenRouter
import requests
import time
from datetime import date, timedelta

# Personal imports
from email_handler import send_email
from article_vetter import vet_articles
from data_cleaner import get_human_legible_txt
from vibe_checker import get_gossip_sentiment
from ai_orchestrator import AIOrchestrator

tavily_client = TavilyClient(api_key=os.getenv("Tavily_DEV"))
ai = AIOrchestrator()

# Initial search
# with open('five_potential_sources.json', 'r', encoding='utf-8') as file:
#     response = json.load(file)

response = tavily_client.search("OpenAI OR Anthropic OR Google DeepMind OR Meta AI OR Mistral OR xAI OR AI OR Artificial Intelligence", topic="news", time_range="day", max_results="5")

def viewResponse(title, url, content, score, published_date, formatter=""):
    print(formatter + "Title\n" + formatter + title + "\n")
    print(formatter + "url: " + url + "\n")
    print(formatter + "Content\n" + formatter + content + "\n")
    print(formatter + "Relevance: " + score + "\n")
    print(formatter + "Published: " + published_date + "\n")
    print(formatter + "---------------------------------------")

# # Vet Article Sources to obtain corroborate and consequential sources for the newsletter.
temp_email_results = vet_articles(response, tavily_client, ai)

vetted_article_titles = [d["title"] for d in temp_email_results]
vetted_article_urls = [d["url"] for d in temp_email_results]
        
print("*************************************************************************************************")
print("VALIDATED RESULTS:")
signal_sources_txt = []
# temp_email_results = response["corroborated_consequential_sources"]
for validResult in temp_email_results:
    viewResponse(validResult["title"], validResult["url"], validResult["content"], str(validResult["score"]), str(validResult["published_date"]))
    extract_text = tavily_client.extract(validResult["url"])
    signal_sources_txt.append(extract_text)

# Data cleaning
human_readable_source_txt = get_human_legible_txt(signal_sources_txt)

# Summarize each source
source_summaries = []
# source_summaries = response["source_summaries2"]
for source in human_readable_source_txt:
    prompt = """Summarize the following source in 120–150 words.""" + source

    summary_result = ai.generate(prompt, "open_router")
    print(summary_result)
    source_summaries.append(summary_result)
    print()

# --------------------------------------------------------------------------------------------------
# RETRIEVE GOSSIP - X and Reddit
# REDDIT: https://www.reddit.com/r/opencodeCLI/comments/1w4jwih/anthropic_just_released_claude_fable_51_and
# X: https://x.com/ArtificialAnlys/status/2094881171066978525

unfiltered_gossip = get_gossip_sentiment(vetted_article_titles, tavily_client, ai)

# --------------------------------------------------------------------------------------------------
# GitHub Repo of the Day

days_ago = 7
target_date = date.today() - timedelta(days=days_ago)
search_date = str(target_date.isoformat())
github_query = "https://api.github.com/search/repositories?q=created:>"+search_date+"&sort=stars&order=desc&topic=ai"
top_repo = requests.get(github_query)

print("GitHub Search")

repo = top_repo.json()["items"][0]

github_repo_of_the_day = {
    "name": repo.get("name"),
    "url": repo.get("html_url"),
    "description": repo.get("description"),
    "homepage": repo.get("homepage"),
    "stars": repo.get("stargazers_count"),
    "language": repo.get("language")
}

print(github_repo_of_the_day)

# --------------------------------------------------------------------------------------------------
# Newsletter Generation!!!
# Combine all the info to create the newsletter.
# Prompt = Article Summaries + Gossip Sentiments + GitHub Repo of the Day

news_info = ""
for i in range(0, len(vetted_article_titles)):
    news_info += "Article Title: " + vetted_article_titles[i] + "\n"
    news_info += "Article URL: " + vetted_article_urls[i] + "\n"
    news_info += "Article Info:\n"
    news_info += source_summaries[i] + "\n\n"


ultimate_prompt = "Create a markdown formatted newsletter with a reading time of about four minutes. " 
ultimate_prompt += "The audience of this newsletter are smart, curious, non-technical business owners. " 
ultimate_prompt += "The newsletter should contain the following sections with relevant information:\n\n " 

ultimate_prompt += "The Big Story\n"
ultimate_prompt += "The one thing that matters most today, and why.\n\n"

ultimate_prompt += "Frontier Watch\n" 
ultimate_prompt += "A sentence on how what each source is about and how it relates to at least two of the following: "
ultimate_prompt += "time saved, costs reduced, or revenue unlocked. Be specific when talking about what parts specifically "  
ultimate_prompt += "relate to the time saved, costs reduced, or revenue unlocked. Include hyperlinks to the relevant article "  
ultimate_prompt += "the content was sourced from. Include any other relevant information from these sources you deem worth "
ultimate_prompt += "knowing.\n"
ultimate_prompt += "Sources:\n"
ultimate_prompt += news_info

ultimate_prompt += "The Street Says\n"
ultimate_prompt += "Sentiment, gossip, and hot takes from X and Reddit.\n"
ultimate_prompt += "X:\n"
ultimate_prompt += unfiltered_gossip["x"]["gossip_sentiment"] + "\n"
ultimate_prompt += "Reddit:\n"
ultimate_prompt += unfiltered_gossip["reddit"]["gossip_sentiment"] + "\n\n"

ultimate_prompt += "Repo of the Day\n"
ultimate_prompt += "Information on one GitHub project worth knowing about. Use the following information provided for the "
ultimate_prompt += "GitHub repo of the day.\n"
ultimate_prompt += str(github_repo_of_the_day) + "\n\n"

ultimate_prompt += "Two Steps Ahead\n"
ultimate_prompt += "A short forward-looking take: what today's news hints at for tomorrow."

print("##############################################################################################")
print(ultimate_prompt)
print("##############################################################################################")
print()

newsletter_message = ai.generate(ultimate_prompt, "nvidia", "advanced")

message = markdown.markdown(newsletter_message)

# --------------------------------------------------------------------------------------------------
# SEND EMAIL

print("****************************************************************************")
print("SENDING")
print(message)

send_email(message)