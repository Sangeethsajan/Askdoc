from fastapi import FastAPI
from app.Chat.routes import chat_router
from app.VideoQA.routes import video_router
from fastapi.middleware.cors import CORSMiddleware


origins = [
    "http://localhost:3000",
    "http://172.190.112.201:3000",
    "https://videoqa.vercel.app/",
    "https://askdoc.vercel.app/"
]

version = "v1"

description = """
A REST API for a Q&A Chatbot.

This REST API is able to;
- Create Read Update And delete books
- Add reviews to books
- Add tags to Books e.t.c.
    """

version_prefix =f"/api/{version}"

app = FastAPI(
    title="AskDoc API",
    description=description,
    version=version,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Sangeeth Sajan Baby",
        "url": "https://sangeethsajan.github.com/",
        "email": "sangeethsajan13@gmail.com",
    }
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router, prefix="/chat")
app.include_router(video_router, prefix="/videoqa")

