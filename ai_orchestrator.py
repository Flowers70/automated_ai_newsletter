import os
import requests
import json
import re
from google import genai
from mistralai.client import Mistral
from openrouter import OpenRouter
# from pydantic import BaseModel

class GoogleAdapter:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("Google_AI_Key"))
        self.models = {
            "default": "gemini-3.6-flash",
            "classification": "gemini-3.7-flash",
            "advanced": "gemini-3.8-flash"
        }

    def run(self, prompt, model="default", structured=False):
        response = self.client.interactions.create(
            model=self.models[model],
            input=prompt
        )

        return response.output_text

class MistralAdapter:
    def __init__(self):
        self.client = Mistral(os.getenv("MISTRAL_AI_KEY"))
        self.models = {
            "default": "mistral-small-latest",
            "classification": "mistral-medium-latest",
            "advanced": "mistral-large-2512"
        } 

    def run(self, prompt, model="default", structured=False):
        response = self.client.chat.complete(
            model=self.models[model],
            messages={
                "role": "user",
                "content": prompt
            }
        )

        return response.choices[0].message.content

class OpenRouterAdapter:
    def __init__(self):
        self.client = OpenRouter(api_key=os.getenv("OPENROUTER"))
        self.models = {
            "default": "nvidia/nemotron-3-super-120b-a12b:free",
            "classification": "nvidia/nemotron-3.5-lightning:free",
            "advanced": "nvidia/nemotron-3-ultra-550b-a55b:free"
        }

    def run(self, prompt, model="default", structured=False):
        if not structured:
            response = self.client.chat.send(
                model=self.models[model],
                messages=[
                    {
                        "content": prompt,
                        "role": "user"
                    }
                ],
                stream=False
            )
        else:
            response = self.client.chat.send(
                model=self.models[model],
                messages=[
                    {
                        "content": prompt,
                        "role": "user"
                    }
                ],
                response_format={ # json.loads(response returned)
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

        return response.choices[0].message.content

class NvidiaAdapter:
    def __init__(self):
        self.key = os.getenv("NVIDIA_DEV")
        self.models = {
            "default": "deepseek-v4-pro-0813",
            "classification": "nemotron-3.5-lightning-30b-a3b",
            "advanced": "nvidia/nemotron-3-ultra-550b-a55b"
        }

    def run(self, prompt, model="default", structured=False):
        nvidia_endpoint = "https://integrate.api.nvidia.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.models[model],
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = requests.post(
            nvidia_endpoint,
            headers=headers,
            json=payload,
        )

        data = response.json()

        return data["choices"][0]["message"]["content"]

class AIOrchestrator:
    def __init__(self):
        self.providers = {
            "google": GoogleAdapter(),
            "mistral": MistralAdapter(),
            "open_router": OpenRouterAdapter(),
            "nvidia": NvidiaAdapter()
        }
        self.fallback_order = ["nvidia", "mistral", "open_router", "google"]
        self.model_order = ["default", "advanced", "classification"]

    def _retry(self, prompt, provider, model, structured):
        try:
            return self.providers[provider].run(prompt, model, structured)
        except Exception as e:
            print("Initial requested provider unavailable:", provider)
            pass

        other_models = [m for m in self.model_order if m != model]
        for i in range(0, len(self.model_order)):
            if i == 0:
                active_model = model 
            else:
                active_model = other_models[i-1]

            for fallback in self.fallback_order:
                if fallback == provider and active_model == model:
                    continue
                try:
                    return self.providers[fallback].run(prompt, active_model, structured)
                except Exception:
                    continue

        raise Exception("All providers failed.")

    def generate(self, prompt, provider=None, model="default", structured=False):
        raw_results = self._retry(prompt, provider, model, structured)
        if not structured:
            return raw_results
            
        try:
            data = json.loads(raw_results)

            if isinstance(data, dict) and "categories" in data:
                return data["categories"]
            # If the model returned a single category
            if isinstance(data, dict) and "category" in data:
                return [data["category"]]
        except Exception:
            pass

        text = raw_results.lower()
        return re.findall(r'\b(news|analysis|noise)\b', text)
        
    