from ..database import get_supabase
from typing import List
class DocumentService:
    def __init__(self):
        with get_supabase() as supabase:
            self.supabase = supabase
    async def save_document(self, tablename: str, content: List[dict]):
        print(content)
        try:
            response = self.supabase.table(tablename).insert(content).execute()
            return response.data[0]
        except Exception as e:
            print(f"Error saving document: {e}")
            raise

    async def get_user_documents(self, user_id: str):
        try:
            response = self.supabase.table('documents').select('*').eq('user_id', user_id).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching documents: {e}")
            raise

    async def delete_user_documents(self, document_list: List[str]):
        try:
            response = self.supabase.table('documents').delete().in_('id', document_list).execute()
            return response.data
        except Exception as e:
            print(f"Error deleting documents: {e}")
            raise