import os
import json
from openrouter import OpenRouter

def vet_articles(response, open_router_model, tavily_client):
    # Determine if it is just a SEO junk like "Top Multimodal AI Companies in 2026 Google OpenAI"
    # For this to perform well as expected in the coding challenge debrief it will need to implement
    # a LLM.
    
    article_titles = [d["title"] for d in response["results"]]

    prompt = """
            Classify these articles into one of three categories. 
            News - reporting a specific event, discovery, release, or factual claim. 
            Analysis - offering insight, perspective, or interpretation about AI trends.
            Noise - generic SEO filler, listicles, hype, or non‑consequential content.
            Respond with a csv list containing one word for each article: news, analysis, or noise.

            Title: """+str(article_titles)

    # quality_analysis = mistral_client.chat.parse(
    #     model="mistral-small-latest",
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": prompt
    #         }
    #     ],
    #     response_format=CategoryList,
    #     temperature=0
    # )

    # nvidia/nemotron-3-super-120b-a12b:free
    # google/gemma-4-31b-it:free

    with OpenRouter(
        api_key = os.getenv("OPENROUTER")
    ) as open_router:
        quality_analysis = open_router.chat.send(
            model=open_router_model,
            messages = [
                {
                    "content": prompt,
                    "role": "user"
                }
            ],
            response_format={
                "type":"json_schema",
                "json_schema": {
                    "name": "quality_json",
                    "strict": True,
                    "schema": {
                        "type":"object",
                        "properties": {
                            "categories": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["categories"]
                    }
                }
            },
            stream=False
        )

    print(quality_analysis.choices[0].message.content)

    # quality_results = response["quality_results"]
    quality_results = quality_analysis.choices[0].message.content
    quality_results = json.loads(quality_results)

    quality_results = quality_results["categories"]

    print("Looking at:", quality_results, type(quality_results))

    # Identify 3 corroborate articles to ensure this isn't a one off source
    temp_email_results = []
    for pageI in range(0, len(response["results"])):
        if(quality_results[pageI] != "noise"):

            first_sentence = response["results"][pageI]["content"].split(".")[0]
            search_query = response["results"][pageI]["title"] + " " + first_sentence

            corroborate_search_results = tavily_client.search(search_query, topic="news")
            # print("Articles #:", len(corroborate_search_results["results"]))

            corroborate_evidence = 0
            for subPage in corroborate_search_results["results"]:
                if subPage["score"] >= 0.5 and subPage["url"] != response["results"][pageI]["url"]:
                    corroborate_evidence += 1

            if corroborate_evidence >= 3:
                # The article is co"rroborate and should be included in the newsletter. 
                print(response["results"][pageI]["title"], "|", response["results"][pageI]["url"])
                print("Corroborated")
                print()
                temp_email_results.append(response["results"][pageI]) 

        if(len(temp_email_results) >= 3):
            print("Length of 3 met.")
            break

    return temp_email_results