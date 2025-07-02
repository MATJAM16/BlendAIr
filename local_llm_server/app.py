"""Lightweight FastAPI server that emulates the Edge Function locally.
Run with:  uvicorn app:app --reload
"""
from fastapi import FastAPI
from pydantic import BaseModel
import os
import openai


class PromptIn(BaseModel):
    prompt: str


app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY", "")

SYSTEM_MSG = (
    "You are a Blender Python assistant. Convert the user prompt into a safe "
    "Python script that manipulates the active scene. Do not import os, subprocess, "
    "or perform network calls."
)


@app.post("/generate")
async def generate(data: PromptIn):
    if not openai.api_key:
        return {"script": "# OPENAI_API_KEY not set"}
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": SYSTEM_MSG}, {"role": "user", "content": data.prompt}],
        max_tokens=300,
    )
    script = resp.choices[0].message.content
    return {"script": script}
