# import json

def vet_articles(response, tavily_client, ai):
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

    quality_results = ai.generate(prompt, "open_router", "classification", True)
    # quality_results = json.loads(quality_results)

    # quality_results = quality_results["categories"]

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