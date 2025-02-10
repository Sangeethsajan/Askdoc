from fastapi import APIRouter, File, UploadFile, Form, Response
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List
import uuid
import json
from app.Chat.db_services import DocumentService
from app.Chat.services import loadPdf,searchPineconeIndex, generateLLLMOutput, LLMResponse, deletePineconeIndex
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
import os
from openai import OpenAI
import ast
from dotenv import load_dotenv
load_dotenv()

chat_router = APIRouter()
doc_service = DocumentService()

@chat_router.post("/load_docs/")
async def load_docs(files: List[UploadFile] = File(...),user_id: str = Form(...)):
    try:
        await loadPdf(files,uuid.UUID(user_id))  
    except Exception as e:
        return Response(content=f"Error: {e}", status_code=500)
    return Response(content="Files Uploaded", status_code=201)

@chat_router.post("/ask/")
async def ask(query: str = Form(...), document_list: str = Form(...)):
    try:
        sources = []
        document_list = json.loads(document_list)
        value = await searchPineconeIndex(query,document_list)
        #result = await generateLLLMOutput(value,query)
        for val in value:
            sources.append({"metadata":{"content": val["metadata"]["content"],
                                        "filename": val["metadata"]["file_name"],
                                        "page_number": val["metadata"]["page_number"]}
                                        })
        async def generate():
            async for chunk in LLMResponse(value, query):
                if chunk:
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            yield f"data: {json.dumps({'sources': sources})}\n\n"
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )

    except Exception as e:
        print(f"Error in ask_doc: {str(e)}")
        async def error_generator():
            yield f"data: {json.dumps({'error':"Error"})}\n\n"
        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream"
        )
    
@chat_router.post("/get_docs/")
async def get_docs(user_id: str = Form(...)):
    try:
        documents = await doc_service.get_user_documents(uuid.UUID(user_id).hex)
    except Exception as e:
        return Response(content=f"Error: {e}", status_code=500)
    return JSONResponse(content=documents, status_code=200)

@chat_router.post("/delete_docs/")
async def delete_docs(user_id: str = Form(...)):
    try:
        documents = await doc_service.get_user_documents(uuid.UUID(user_id).hex)
        documents = [doc["id"] for doc in documents]
        await deletePineconeIndex(documents)
        await doc_service.delete_user_documents(documents)
    except Exception as e:
        return Response(content=f"Error: {e}", status_code=500)
    return Response(content="Documents Deleted", status_code=200)

@chat_router.post("/get_env/")
async def get_env():
    return JSONResponse(content={"api_key": os.environ.get("PINECONE_API_KEY"), "index_host": os.environ.get("PINECONE_INDEX_HOST")}, status_code=200)