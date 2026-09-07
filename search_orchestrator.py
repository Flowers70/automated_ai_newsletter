import os
import time
from tavily import TavilyClient

class SearchOrchestrator:
    def __init__(self):
        self.providers = {
            "tavily": TavilyClient(api_key=os.getenv("Tavily_DEV"))
        }

    def search(self, query, topic="general", time_range=None, max_results=5):
        for attempt in range(3):
            try:
                if time_range == None:
                    return self.providers["tavily"].search(query, topic=topic, max_results=max_results)
                else:
                    return self.providers["tavily"].search(query, topic=topic, time_range=time_range, max_results=max_results)
            except Exception as e:
                print("Tavily search failed attempt #" + (attempt+1) + " " + e)
                time.sleep(2)
        return {"results": []}

    def extract(self, url):
        for attempt in range(3):
            try:
                return self.providers["tavily"].extract(url)
            except Exception as e:
                print("Tavily extract failed attempt #" + (attempt+1) + " " + e)
                time.sleep(2)
        return {"results": []}