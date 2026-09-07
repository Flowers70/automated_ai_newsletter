import os
import requests

class SupabaseStorage:
    def __init__(self, url=None, key=None):
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_PRIVATE_KEY")

        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL or SUPABASE_PRIVATE_KEY missing")

        self.base = f"{self.url}/storage/v1/object"

        self.headers = {
            "Authorization": f"Bearer {self.key}"
        }

    def upload(self, bucket, path, content, content_type="application/octet-stream"):
        """Upload or overwrite a file in Supabase Storage."""
        url = f"{self.base}/{bucket}/{path}"
        headers = {**self.headers, "Content-Type": content_type}

        response = requests.post(url, headers=headers, data=content)
        response.raise_for_status()
        return response.json()

    def download(self, bucket, path):
        """Download a file from Supabase Storage."""
        url = f"{self.base}/{bucket}/{path}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.content

    def upload_json(self, bucket, path, obj):
        """Upload a JSON object."""
        import json
        content = json.dumps(obj, indent=2).encode("utf-8")
        return self.upload(bucket, path, content, "application/json")

    def download_json(self, bucket, path):
        """Download and parse a JSON file."""
        import json
        raw = self.download(bucket, path)
        return json.loads(raw.decode("utf-8"))

    def upload_html(self, bucket, path, html_str):
        """Upload an HTML file."""
        return self.upload(bucket, path, html_str.encode("utf-8"), "text/html")

    def download_html(self, bucket, path):
        """Download an HTML file as text."""
        raw = self.download(bucket, path)
        return raw.decode("utf-8")
