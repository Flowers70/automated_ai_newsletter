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

    # Only return a max of three results to ensure the newsletter can comfortably perform well
    # in talking about the signal while staying within the 5 minute reading mark.
    vetted_articles = []
    for pageI in range(0, len(response["results"])):
        if(quality_results[pageI] != "noise"):

            first_sentence = response["results"][pageI]["content"].split(".")[0]
            search_query = response["results"][pageI]["title"] + " " + first_sentence

            corroborate_search_results = tavily_client.search(search_query, topic="news")

            corroborate_evidence = 0
            for subPage in corroborate_search_results["results"]:
                if subPage["score"] >= 0.5 and subPage["url"] != response["results"][pageI]["url"]:
                    corroborate_evidence += 1

            # Identify 3 corroborate articles to ensure this isn't a one off source
            if corroborate_evidence >= 3:
                vetted_articles.append(response["results"][pageI]) 

        if(len(vetted_articles) >= 3):
            print("Length of 3 met.")
            break

    return vetted_articles