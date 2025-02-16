from app.VideoQA.models import VideoQARequest
from fastapi import HTTPException
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import googleapiclient.discovery
from google.oauth2 import service_account
from youtube_transcript_api import YouTubeTranscriptApi
import pinecone
from openai import OpenAI,AsyncOpenAI
import json
import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
GOOGLE_CREDS = json.loads(os.environ.get("GOOGLE_CREDS"))
async def startProcessing(request: VideoQARequest):
    try:

        # 1. Get video URLs from sheet
        video_urls = await get_sheet_data(request.video_sheet_url)
        
        # 2. Get transcripts
        transcripts = await get_video_transcripts(video_urls)
        
        # 3. Create embeddings and store
        #transcript_embeddings = await store_embeddings(transcripts)
        
        # 4. Get questions from doc
        questions = await get_questions_from_doc(request.question_doc_url)
        
        # 5. Process with LLM
        answers = await process_with_llm(questions, transcripts, request.llm_prompt)

        # 6. Write to output doc
        await write_to_doc(answers, request.output_doc_url)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def get_sheet_data(sheet_url: str) -> List[str]:
    """
    Connect to Google Sheets API and extract video URLs
    """
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = service_account.Credentials.from_service_account_info(GOOGLE_CREDS, scopes=SCOPES)
    
    service = build('sheets', 'v4', credentials=creds)
    
    # Extract sheet ID from URL
    sheet_id = extract_sheet_id(sheet_url)
    
    # Get video URLs from sheet
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range='A1:A3'  # Assuming URLs are in column B
    ).execute()
    
    values = result.get('values', [])
    return [row[0] for row in values]  # Skip header row

def extract_sheet_id(sheet_url: str) -> str:
    """
    Extract Sheet ID from Google Sheets URL.
    Works with both old and new Google Sheets URL formats.
    
    Examples:
    - https://docs.google.com/spreadsheets/d/1234567890abcdef/edit#gid=0
    - https://docs.google.com/spreadsheets/d/1234567890abcdef/edit?usp=sharing
    """
    try:
        # Split URL by '/'
        parts = sheet_url.split('/')
        # Sheet ID is always after '/d/' in the URL
        for i, part in enumerate(parts):
            if part == 'd':
                return parts[i + 1].split('/')[0]
        raise ValueError("Could not find sheet ID in URL")
    except Exception as e:
        raise ValueError(f"Invalid Google Sheets URL: {str(e)}")

def extract_doc_id(doc_url: str) -> str:
    """
    Extract Document ID from Google Docs URL.
    Works with both old and new Google Docs URL formats.
    
    Examples:
    - https://docs.google.com/document/d/1234567890abcdef/edit
    - https://docs.google.com/document/d/1234567890abcdef/edit?usp=sharing
    """
    try:
        parts = doc_url.split('/')
        for i, part in enumerate(parts):
            if part == 'd':
                return parts[i + 1].split('/')[0]
        raise ValueError("Could not find document ID in URL")
    except Exception as e:
        raise ValueError(f"Invalid Google Docs URL: {str(e)}")

def extract_video_id(video_url: str) -> str:
    """
    Extract Video ID from YouTube URL.
    Supports multiple YouTube URL formats.
    
    Examples:
    - https://www.youtube.com/watch?v=1234567890ab
    - https://youtu.be/1234567890ab
    - https://www.youtube.com/embed/1234567890ab
    """
    try:
        if 'youtu.be' in video_url:
            return video_url.split('/')[-1].split('?')[0]
        elif 'watch?v=' in video_url:
            return video_url.split('watch?v=')[1].split('&')[0]
        elif 'embed/' in video_url:
            return video_url.split('embed/')[1].split('?')[0]
        else:
            raise ValueError("Unrecognized YouTube URL format")
    except Exception as e:
        raise ValueError(f"Invalid YouTube URL: {str(e)}")
    
async def get_video_transcripts(video_urls: List[str]) -> List[dict]:
    """
    Extract transcripts from YouTube videos
    """
    transcripts = []
    
    for url in video_urls:
        video_id = extract_video_id(url)
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcripts.append({
                'video_id': video_id,
                'url': url,
                'transcript': ' '.join([entry['text'] for entry in transcript])
            })
        except Exception as e:
            print(f"Error getting transcript for {url}: {str(e)}")
    
    return transcripts

async def get_questions_from_doc(doc_url: str) -> List[str]:
    """
    Extract questions from Google Doc.
    Assumes each question is on a new line or numbered/bulleted.
    """
    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
    creds = service_account.Credentials.from_service_account_info(GOOGLE_CREDS, scopes=SCOPES)
    
    service = build('docs', 'v1', credentials=creds)
    doc_id = extract_doc_id(doc_url)
    
    try:
        # Get the document content
        document = service.documents().get(documentId=doc_id).execute()
        
        # Extract text content
        questions = []
        content = document.get('body').get('content')
        
        for element in content:
            if 'paragraph' in element:
                paragraph = element.get('paragraph')
                text = ''
                
                # Concatenate all text runs in the paragraph
                for run in paragraph.get('elements'):
                    if 'textRun' in run:
                        text += run.get('textRun').get('content')
                
                # Clean and add non-empty questions
                text = text.strip()
                if text and not text.isspace():
                    # Remove any question numbers or bullets
                    text = text.lstrip('1234567890.- ')
                    questions.append(text)
        print(questions)
        return questions

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting questions from doc: {str(e)}"
        )

async def process_with_llm(questions: List[str], transcripts: List[dict], llm_prompt: Optional[str]):
    try:
        """
        Process questions with LLM using transcripts
        """
        answers = []
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "I'm giving  you muiltiple video transcripts don't answer right now, After this I will send the questions, then you can answer based on the context:"},
                ]
            )

        for transcript in transcripts:
            response =  client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": transcript['transcript']},
                ]
            )

        for question in questions:
            # Construct prompt
        
            # Get LLM response
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Answer the following question based on the context given above:"},
                    {"role": "user", "content": question + llm_prompt}
                ]
            )
        
            answers.append({
                'question': question,
                'answer': response.choices[0].message.content,
            })
    
        return answers
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing with LLM: {str(e)}"
        )

async def write_to_doc(answers: List[dict], doc_url: str):
    """
    Write answers to Google Doc
    """
    SCOPES = ['https://www.googleapis.com/auth/documents']
    creds = service_account.Credentials.from_service_account_info(GOOGLE_CREDS, scopes=SCOPES)
    
    service = build('docs', 'v1', credentials=creds)
    doc_id = extract_doc_id(doc_url)
    
    requests = []
    for answer in answers[::-1]:
        requests.extend([
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': f"Q: {answer['answer']}\n\n"
                }
            },
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': f"A: {answer['question']}\n\n"
                }
            }
        ])
    
    service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()