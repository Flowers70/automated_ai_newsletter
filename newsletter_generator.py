import os
from tavily import TavilyClient
from google import genai
from mistralai.client import Mistral
import json
from pydantic import BaseModel
import markdown
from openrouter import OpenRouter
import requests
import time
from datetime import date, timedelta

# Personal imports
from email_handler import send_email
from article_vetter import vet_articles
from data_cleaner import get_human_legible_txt
from vibe_checker import get_gossip_sentiment

tavily_key = os.getenv("Tavily_DEV")
tavily_client = TavilyClient(api_key=tavily_key)

google_key = os.getenv("Google_AI_Key")
google_client = genai.Client(api_key=google_key)

mistral_key = os.getenv("MISTRAL_AI_KEY")
mistral_client = Mistral(mistral_key)

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
open_router_model = "nvidia/nemotron-3-super-120b-a12b:free"
temp_email_results = vet_articles(response, open_router_model, tavily_client)

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

    # summary = mistral_client.chat.complete(
    #     model="mistral-small-latest",
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": prompt
    #         }
    #     ]
    # )

    with OpenRouter(
        api_key = os.getenv("OPENROUTER")
    ) as open_router:
        summary = open_router.chat.send(
            model=open_router_model,
            messages = [
                {
                    "content": prompt,
                    "role": "user"
                }
            ],
            stream=False
        )

    summary_result = summary.choices[0].message.content
    print(formatted_output)
    source_summaries.append(formatted_output)
    print()

# --------------------------------------------------------------------------------------------------
# RETRIEVE GOSSIP - X and Reddit
# REDDIT: https://www.reddit.com/r/opencodeCLI/comments/1w4jwih/anthropic_just_released_claude_fable_51_and
# X: https://x.com/ArtificialAnlys/status/2094881171066978525

unfiltered_gossip = get_gossip_sentiment(vetted_article_titles, open_router_model, tavily_client)

# NOTE On Reddit - There is no way to anonymously scrape Reddit in Python
# Instead create a JavaScript/Typescript part that uses Devvit to get the info needed.
# You've got this you are so close! Keep going :)

# --------------------------------------------------------------------------------------------------
# GitHub Repo of the Day
# GET https://github.com:>2026-08-01&sort=stars&order=desc
# https://api.github.com/search/repositories?q=created:>2026-08-01&sort=stars&order=desc

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

nvidia_endpoint = "https://integrate.api.nvidia.com/v1/chat/completions"

NVIDIA_API_KEY = os.getenv("NVIDIA_DEV")

headers = {
    "Authorization": f"Bearer {NVIDIA_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "nvidia/nemotron-3-ultra-550b-a55b",
    "messages": [
        {
            "role": "user",
            "content": ultimate_prompt
        }
    ]
}

response = requests.post(
    nvidia_endpoint,
    headers=headers,
    json=payload,
)

print(response)
data = response.json()
print("DATA:", data)
newsletter_message = data["choices"][0]["message"]["content"]

# newsletter_message = google_client.interactions.create(
#     model="gemini-3.8-flash",
#     input=ultimate_prompt
# )

# newsletter_message = newsletter_message.output_text

message = markdown.markdown(newsletter_message)

# --------------------------------------------------------------------------------------------------
# SEND EMAIL

print("****************************************************************************")
print("SENDING")
print(message)

send_email(message)