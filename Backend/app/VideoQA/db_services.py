from ..database import get_supabase
from typing import List
class DocumentService:
    def __init__(self):
        with get_supabase() as supabase:
            self.supabase = supabase
            
    async def save_flow(self, tablename: str, content: List[dict]):
        print(content)
        try:
            response = self.supabase.table(tablename).insert(content).execute()
            return response.data[0]
        except Exception as e:
            print(f"Error saving document: {e}")
            raise
    
    async def get_flows(self, user_id: str):
        try:
            response = self.supabase.table('videosflows').select('*').eq('user_id', user_id).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching documents: {e}")
            raise

    async def get_flow_details(self, flow_id: str):
        try:
            response = self.supabase.table('videosflows').select('*').eq('flow_id', flow_id).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching documents: {e}")
            raise

    async def delete_flow(self, flow_id: str):
        try:
            response = self.supabase.table('videosflows').delete().eq('flow_id', flow_id).execute()
            return response.data
        except Exception as e:
            print(f"Error deleting documents: {e}")
            raise