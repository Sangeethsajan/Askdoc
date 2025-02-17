from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import JSONResponse

from typing import Optional
import uuid

from app.VideoQA.models import VideoQARequest,CreateFlowRequest
from app.VideoQA.services import startProcessing
from app.VideoQA.db_services import DocumentService

from dotenv import load_dotenv
load_dotenv()

video_router = APIRouter()
db_service = DocumentService()

@video_router.post("/create-flow/")    
async def create_flow(
    video_sheet_url: str = Form(...),
    question_doc_url: str = Form(...),
    llm_prompt: Optional[str] = Form(None),
    output_doc_url: str = Form(...),
    user_id: str = Form(...),
    flow_name: str = Form(...)):
        documetList = [{"flow_id":uuid.uuid4().hex,
                        "video_sheet_url":video_sheet_url,
                        "question_doc_url":question_doc_url,
                        "llm_prompt":llm_prompt,
                        "output_doc_url":output_doc_url,
                        "user_id":uuid.UUID(user_id).hex,
                        "flow_name":flow_name}]
        await db_service.save_flow("videosflows",documetList)
        return JSONResponse(content={"message": "Flow created successfully","status":"success"}, status_code=201)

@video_router.post("/get-flows/")
async def get_flows(user_id: str = Form(...)):
    user_id = uuid.UUID(user_id).hex
    flows = await db_service.get_flows(user_id)
    return JSONResponse(content=flows, status_code=200)

@video_router.post("/run-flow/")
async def run_flow(flow_id: str = Form(...)):
    try:
        flow_id = uuid.UUID(flow_id).hex
        flows = await db_service.get_flow_details(flow_id)
        request_data = VideoQARequest(
            video_sheet_url=flows[0]['video_sheet_url'],
            question_doc_url=flows[0]['question_doc_url'],
            llm_prompt=flows[0]['llm_prompt'],
            output_doc_url=flows[0]['output_doc_url'],
        )
        await startProcessing(request_data)
        return JSONResponse(content={"message": "Flow completed successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@video_router.post("/delete-flow/")
async def delete_flow(flow_id: str = Form(...)):
    try:
        flow_id = uuid.UUID(flow_id).hex
        await db_service.delete_flow(flow_id)
        return JSONResponse(content={"message": "Flow deleted successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
