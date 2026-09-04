import os
from tavily import TavilyClient
from google import genai
from mistralai.client import Mistral
import json

import smtplib # For email
from email.message import EmailMessage

import spacy # For NLP (Natural Language Processing)

tavily_key = os.getenv("Tavily_DEV")
tavily_client = TavilyClient(api_key=tavily_key)

google_key = os.getenv("Google_AI_Key")
google_client = genai.Client(api_key=google_key)

mistral_key = os.getenv("MISTRAL_AI_KEY")
mistral_client = Mistral(mistral_key)

# Initial search
with open('five_potential_sources.json', 'r', encoding='utf-8') as file:
    response = json.load(file)
# response = tavily_client.search("OpenAI OR Anthropic OR Google DeepMind OR Meta AI OR Mistral OR xAI OR AI OR Artificial Intelligence", topic="news", time_range="day")

def viewResponse(title, url, content, score, published_date, formatter=""):
    print(formatter + "Title\n" + formatter + title + "\n")
    print(formatter + "url: " + url + "\n")
    print(formatter + "Content\n" + formatter + content + "\n")
    print(formatter + "Relevance: " + score + "\n")
    print(formatter + "Published: " + published_date + "\n")
    print(formatter + "---------------------------------------")


# Determine if it is just a SEO junk like "Top Multimodal AI Companies in 2026 Google OpenAI"
# For this to perform well as expected in the coding challenge debrief it will need to implement
# a LLM.

# article_titles = [d["title"] for d in response["results"]]
# prompt = """
#         Classify these articles into one of three categories. 
#         News - reporting a specific event, discovery, release, or factual claim. 
#         Analysis - offering insight, perspective, or interpretation about AI trends.
#         Noise - generic SEO filler, listicles, hype, or non‑consequential content.
#         Respond with a list containing one word for each article: news, analysis, or noise.

#         Title: """+str(article_titles)

# quality_analysis = mistral_client.chat.complete(
#     model="mistral-small-latest",
#     messages=[
#         {
#             "role": "user",
#             "content": prompt
#         }
#     ]
# )

# print(quality_analysis.choices[0].message.content)

quality_results = response["quality_results"]

# # Identify 3 corroborate articles to ensure this isn't a one off source
# temp_email_results = []
# for pageI in range(0, len(response["results"])):
#     print(response["results"][pageI]["title"], "|", response["results"][pageI]["url"])
#     if(quality_results[pageI] != "noise"):

#         first_sentence = response["results"][pageI]["content"].split(".")[0]
#         search_query = response["results"][pageI]["title"] + " " + first_sentence

#         corroborate_search_results = tavily_client.search(search_query, topic="news")
#         print("Articles #:", len(corroborate_search_results["results"]))

#         corroborate_evidence = 0
#         for subPage in corroborate_search_results["results"]:
#             if subPage["score"] >= 0.5 and subPage["url"] != response["results"][pageI]["url"]:
#                 corroborate_evidence += 1

#         if corroborate_evidence >= 3:
#             # The article is co"rroborate and should be included in the newsletter. 
#             print("Corroborated")
#             temp_email_results.append(response["results"][pageI]) 

#     if(len(temp_email_results) >= 3):
#         print("Length of 3 met.")
#         break
        
print("*************************************************************************************************")
print("VALIDATED RESULTS:")
signal_sources_txt = []
temp_email_results = response["corroborated_consequential_sources"]
for validResult in temp_email_results:
    extract_text = tavily_client.extract(validResult["url"])
    signal_sources_txt.append(extract_text)

# print("TEXT:")
# # Perform NLP to extract human readible text scraped from the signal source.
# for signal_source in signal_sources_txt:
#     print(signal_source)
#     print()

nlp = spacy.blank("en")
nlp.add_pipe("sentencizer")

# Time to clean extracted data to something a human can read.
# Step 1 - VERBS AND NOUNS
nlp = spacy.load("en_core_web_sm")

def has_verb_and_noun(sent):
    doc = nlp(sent)
    has_verb = any(t.pos_ == "VERB" for t in doc)
    has_noun = any(t.pos_ in ("NOUN", "PROPN") for t in doc)
    return has_verb and has_noun

def has_lowercase_word(sent):
    return any(word.islower() for word in sent.split())

# Step 2 - PUNCTUATION
import string

def has_punctuation(sent):
    return any(char in string.punctuation for char in sent)

# Step 3 - LENGTH
def long_enough(sent):
    return len(sent.split()) > 6

# Step 4 - NOT SYMBOL DENSE
def not_symbol_heavy(sent):
    symbols = sum(not c.isalnum() and not c.isspace() for c in sent)
    return symbols / max(len(sent), 1) < 0.3

# Calculate Sentence Score
def is_human_readable(sent):
    return(
        has_verb_and_noun(sent)
        and has_lowercase_word(sent)
        and long_enough(sent)
        and not_symbol_heavy(sent)
        and has_punctuation(sent)
    )

human_readable_source_txt = []
for source in signal_sources_txt:
    # doc = nlp(signal_sources_txt[0]["results"][0]["raw_content"])
    candidate_sentences = [sent.strip() for sent in source["results"][0]["raw_content"].split("\n") if sent.strip()]

    # Filter
    human_sentences = [s for s in candidate_sentences if is_human_readable(s)]
    human_text = "\n".join(human_sentences)
    human_readable_source_txt.append(human_text)

# Summarize each source
source_summaries = []
source_summaries = response["source_summaries"]
# for source in human_readable_source_txt:
#     prompt = """Summarize the following source in 120–150 words.""" + source

#     summary = mistral_client.chat.complete(
#         model="mistral-small-latest",
#         messages=[
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ]
#     )

#     print(summary.choices[0].message.content)
#     source_summaries.append(summary.choices[0].message.content)
#     print()

# --------------------------------------------------------------------------------------------------
# RETRIEVE GOSSIP - X and Reddit
# REDDIT: https://www.reddit.com/r/opencodeCLI/comments/1w4jwih/anthropic_just_released_claude_fable_51_and
# X: https://x.com/ArtificialAnlys/status/2094881171066978525
reddit_gossip = tavily_client.search("site:reddit.com Claude Fable 5.1 (max with fallback)")
x_gossip = tavily_client.search("site:x.com Claude Fable 5.1 (max with fallback)")

print("Reddit:")
print(reddit_gossip["results"])
print()
print("---")
print()
print("X:")
print(x_gossip["results"])

# --------------------------------------------------------------------------------------------------
# SEND EMAIL

# EMAIL_ADDRESS = os.environ.get("EMAIL_USER")
# EMAIL_PASSWORD = os.environ.get("EMAIL_PASS")

# msg = EmailMessage()
# msg["Subject"] = "AI Newsletter"
# msg["From"] = EMAIL_ADDRESS
# msg["To"] = EMAIL_ADDRESS
# msg.set_content("Hello World! " + str(temp_email_results))

# with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
#     smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#     smtp.send_message(msg)