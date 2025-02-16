from typing import Optional
from pydantic import BaseModel

class VideoQARequest(BaseModel):
    video_sheet_url: str
    question_doc_url: str
    llm_prompt: Optional[str] = None
    output_doc_url: str

class CreateFlowRequest(BaseModel):
    video_sheet_url: str
    question_doc_url: str
    llm_prompt: Optional[str] = None
    output_doc_url: str
    flow_name: str