import json
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core import session_store, state_machine
from integrations import supabase_client

CONFIG_PATH = Path(__file__).parent / "config" / "business_config.json"
with open(CONFIG_PATH) as f:
    BUSINESS_CONFIG = json.load(f)

app = FastAPI(title="Voice Appointment Booking Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    state: str


@app.get("/health")
def health():
    return {"status": "ok", "business_name": BUSINESS_CONFIG["business_name"]}


@app.get("/config")
def get_config():
    return BUSINESS_CONFIG


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session_id = req.session_id or session_store.create_session()
    session = session_store.get_session(session_id)
    if session is None:
        session_id = session_store.create_session()
        session = session_store.get_session(session_id)

    if not req.message or not req.message.strip():
        return ChatResponse(
            session_id=session_id,
            reply="Sorry, I didn't hear anything — could you say that again?",
            state=session["state"],
        )

    reply = state_machine.handle_message(session, req.message.strip(), BUSINESS_CONFIG)
    session_store.save_session(session_id, session)

    return ChatResponse(session_id=session_id, reply=reply, state=session["state"])


@app.get("/appointments")
def get_appointments():
    return supabase_client.list_appointments()


@app.post("/session/new")
def new_session():
    return {"session_id": session_store.create_session()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
