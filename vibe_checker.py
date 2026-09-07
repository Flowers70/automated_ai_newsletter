def get_gossip_sentiment(vetted_article_titles, search, ai):
    unfiltered_gossip = {
        "reddit": {
            "title": [],
            "content": [],
            "url": [],
            "gossip_sentiment": ""
        },
        "x": {
            "title": [],
            "content": [],
            "url": [],
            "gossip_sentiment": ""
        }
    }

    for article_title in vetted_article_titles:
        reddit_gossip = search.search("site:reddit.com Claude Fable 5.1 (max with fallback)", max_results=1)
        x_gossip = search.search("site:x.com Claude Fable 5.1 (max with fallback)", max_results=1)

        unfiltered_gossip["reddit"]["title"].append(reddit_gossip["results"][0]["title"])
        unfiltered_gossip["reddit"]["content"].append(reddit_gossip["results"][0]["content"])
        unfiltered_gossip["reddit"]["url"].append(reddit_gossip["results"][0]["url"])

        unfiltered_gossip["x"]["title"].append(x_gossip["results"][0]["title"])
        unfiltered_gossip["x"]["content"].append(x_gossip["results"][0]["content"])
        unfiltered_gossip["x"]["url"].append(x_gossip["results"][0]["url"])

    if len(unfiltered_gossip["reddit"]["title"]) > 0 and len(unfiltered_gossip["x"]["title"]) > 0:
        for key in unfiltered_gossip:
            prompt = """In a single short paragraph convey the overall sentiment of this gossip: """ + " ".join(unfiltered_gossip[key]["content"])
            unfiltered_gossip[key]["gossip_sentiment"] = ai.generate(prompt, "open_router")
    elif len(unfiltered_gossip["reddit"]["title"]) > 0:
        prompt = """In a single short paragraph convey the overall sentiment of this gossip: """ + " ".join(unfiltered_gossip["reddit"]["content"])
        unfiltered_gossip["reddit"]["gossip_sentiment"] = ai.generate(prompt, "open_router")
        unfiltered_gossip["x"]["gossip_sentiment"] = "No sufficient talk concerning this topic."
    elif len(unfiltered_gossip["x"]["title"]) > 0:
        prompt = """In a single short paragraph convey the overall sentiment of this gossip: """ + " ".join(unfiltered_gossip["x"]["content"])
        unfiltered_gossip["x"]["gossip_sentiment"] = ai.generate(prompt, "open_router")
        unfiltered_gossip["reddit"]["gossip_sentiment"] = "No sufficient talk concerning this topic."
    else:
        unfiltered_gossip["x"]["gossip_sentiment"] = "No sufficient talk concerning this topic."
        unfiltered_gossip["reddit"]["gossip_sentiment"] = "No sufficient talk concerning this topic."

    return unfiltered_gossip