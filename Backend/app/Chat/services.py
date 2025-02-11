from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI,AsyncOpenAI
from pypdf import PdfReader

from fastapi import File, UploadFile,Path
from typing import List
from dotenv import load_dotenv
from pinecone import Pinecone
from pinecone.grpc import PineconeGRPC as PineconeGRPC

from io import BytesIO
import os
import uuid
import ast

from app.Chat.db_services import DocumentService
load_dotenv()

doc_service = DocumentService()

#Move this to separate service
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index(host=os.environ.get("PINECONE_INDEX_HOST"))

async def loadPdf(files:List[UploadFile] = File(...), userid: uuid.UUID = Path(...,title="The ID of the item to get")):
    vectorList = []
    documentList = []

    for File in files:
        DocumentId = uuid.uuid4().hex
        documentList.append({"id": DocumentId, "filename": File.filename,"user_id": userid.hex})

        Content = File.file.read()
        PdfFile = BytesIO(Content)
        Pages = PdfReader(PdfFile)
        
        for PageNum, Page in enumerate(Pages.pages,1):

            VectorEmbeddings, OroginalTextSplits = await createEmbeddings(Page)

            for Index, EmbeddingChunks in enumerate(VectorEmbeddings):
                vectorList.append({
                    "id": uuid.uuid4().hex,
                    "values": EmbeddingChunks,
                    "metadata":{
                        "file_name": File.filename,
                        "page_number": PageNum,
                        "chunk_number": Index,
                        "document_id": DocumentId,
                        "content": OroginalTextSplits[Index]
                    }})
                
    await doc_service.save_document("documents",documentList)
    await createPineconeIndex(vectorList)
    return {"message": "Files Uploaded"}

async def createEmbeddings(file):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # chunk size (characters)
        chunk_overlap=200,  # chunk overlap (characters)
        add_start_index=True,  # track index in original document
    )
    all_splits = text_splitter.split_text(file.extract_text())
    vector = OpenAIEmbeddings(model="text-embedding-3-small")
    
    return vector.embed_documents(all_splits),all_splits

async def createPineconeIndex(vector):
    index.upsert(vector)

async def deletePineconeIndex(documents: List[str]):
    pc = PineconeGRPC(api_key=os.environ.get("PINECONE_API_KEY"))
    
    index = pc.Index(host=os.environ.get("PINECONE_INDEX_HOST"))
    
    results = index.query(
        vector=[0] * 1536,  # your vector dimension
        filter={
            "document_id": {"$in": documents}
        },
        include_metadata=True,
        top_k=10000  # adjust based on how many vectors you expect
    ) 
    vector_ids = [match.id for match in results.matches]
    if vector_ids:
        index.delete(
            ids=vector_ids
        )     

async def searchPineconeIndex(query, document_list):
    try:
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
        enities = await generateEntityOutput(query)

        query_vector = [embeddings.embed_query(entity) for entity in enities]

        processed_results = []
        for query in query_vector:
            results = index.query(
                vector=list(query),
                top_k=2,
                include_metadata=True,
                filter={
                    "document_id": {"$in": document_list}
                }
            )
            for match in results.matches:
                processed_results.append({
                    'score': float(match.score),
                    'metadata': dict(match.metadata),  # Convert metadata to plain dict
                    'id': str(match.id)
                })
        
        return processed_results
        
    except Exception as e:
          # Add logging
        return {"error": str(e)}
    
async def generateEntityOutput(query):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))    

    system_prompt = """'m building a RAG for multiple PDFs. 
    Below is a question, You need to find the search keywords from the question that 
    I need to search in the pinecone database. Just give the keywords in a list 
    separated by commas as a python list. Nothing more."""

    response = client.chat.completions.create(
        model="gpt-4o",  # or your preferred model
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    return ast.literal_eval(response.choices[0].message.content) 

async def LLMResponse(pincone_result, query):
    try:
        client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        context = ""
        for result in pincone_result:
            # Extract text content from metadata
            content = result['metadata'].get('content', '')
            context += f"\nContent: {content}\n"

        system_prompt = """You are a helpful AI assistant answering questions based on the provided context. 
        Use the context to provide accurate answers.If its a generic question like How are you or something like that, answer is appropriately. 
        If the answer cannot be found in the context or provided context doesn't makes sence look for your previous response. If you couldn't find the answer in the previous response,
        just say you don't know the answer and mention that you will try to add some sources that might be helpful."""

        response = await client.chat.completions.create(
            model="gpt-4o",  # or your preferred model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
            ],
            temperature=0.7,
            max_tokens=2000,
            stream=True
        )
        last_content = ""
        
        async for chunk in response:
            if chunk.choices[0].delta.content is not None:
                current_content = chunk.choices[0].delta.content
                # Only yield if it's new content
                if current_content != last_content:
                    last_content = current_content
                    yield current_content
    except Exception as e:
        print(f"Error in LLMRespone: {str(e)}")
        yield f"Error: {str(e)}"

