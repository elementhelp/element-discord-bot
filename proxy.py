from fastapi import FastAPI, Request
from supabase import create_client, Client
import os

app = FastAPI()

# Config supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.post("/report")
async def report(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        job_id = data.get("job_id")

        if not user_id or not job_id:
            return {"error": "Missing user_id or job_id"}

        supabase.table("jobs").insert({
            "user_id": user_id,
            "job_id": job_id
        }).execute()

        return {"status": "ok", "message": "JobId salvat cu succes"}
    except Exception as e:
        return {"error": str(e)}
