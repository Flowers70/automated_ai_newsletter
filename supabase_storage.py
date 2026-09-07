import os
import json
from supabase import create_client

class SupabaseStorage:
    def __init__(self, url=None, key=None):
        self.supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_PRIVATE_KEY"))

    def upload(self, bucket, path, content, content_type="application/octet-stream"):
        response = (
            self.supabase.storage
            .from_(bucket)
            .upload(
                file=content,
                path=path,
                file_options={
                    "content-type": content_type,
                    "upsert": "true"
                }
            )
        )

    def download_json(self, bucket, path):
        file_bytes = (
            self.supabase.storage
            .from_(bucket)
            .download(path)
        )

        data = json.loads(file_bytes)

        return data

    def upload_json(self, bucket, path, obj):
        content = json.dumps(obj, indent=2).encode("utf-8")
        return self.upload(bucket, path, content, "application/json")

    def upload_html(self, bucket, path, html_str):
        return self.upload(bucket, path, html_str.encode("utf-8"), "text/html")
