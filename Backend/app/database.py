import os
from supabase import create_client, Client
from contextlib import contextmanager
from typing import Generator
from dotenv import load_dotenv
load_dotenv()

# For Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@contextmanager
def get_supabase() -> Generator:
    try:
        yield supabase
    except Exception as e:
        print(f"Database error: {e}")
        raise

# For Pinecone
