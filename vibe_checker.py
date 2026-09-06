import os
from openrouter import OpenRouter

def get_gossip_sentiment(vetted_article_titles, open_router_model, tavily_client):
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
        reddit_gossip = tavily_client.search("site:reddit.com Claude Fable 5.1 (max with fallback)", max_results="1")
        x_gossip = tavily_client.search("site:x.com Claude Fable 5.1 (max with fallback)", max_results="1")

        unfiltered_gossip["reddit"]["title"].append(reddit_gossip["results"][0]["title"])
        unfiltered_gossip["reddit"]["content"].append(reddit_gossip["results"][0]["content"])
        unfiltered_gossip["reddit"]["url"].append(reddit_gossip["results"][0]["url"])

        unfiltered_gossip["x"]["title"].append(x_gossip["results"][0]["title"])
        unfiltered_gossip["x"]["content"].append(x_gossip["results"][0]["content"])
        unfiltered_gossip["x"]["url"].append(x_gossip["results"][0]["url"])

    for key in unfiltered_gossip:
        prompt = """In a single short paragraph convey the overall sentiment of this gossip: """ + " ".join(unfiltered_gossip[key]["content"])

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

        unfiltered_gossip[key]["gossip_sentiment"] = summary.choices[0].message.content 

    print("SENTIMENT")
    for key in unfiltered_gossip:
        print(key)
        print(unfiltered_gossip[key]["gossip_sentiment"])
        print()

    return unfiltered_gossip