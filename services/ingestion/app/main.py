import os, uuid, logging
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from shared.db import init_db, execute, fetch_all
from shared.messaging import publish
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
app = FastAPI(title="SentinelMesh Log Ingestion", version="1.0.0")

class LogInput(BaseModel):
    source_ip: str
    username: str = "unknown"
    event_type: str = Field(pattern="^(login_failed|login_success|access_denied|file_access|other)$")
    message: str = ""
    timestamp: datetime | None = None

@app.on_event("startup")
def startup():
    init_db(["""CREATE TABLE IF NOT EXISTS logs (id TEXT PRIMARY KEY, source_ip TEXT NOT NULL, username TEXT NOT NULL, event_type TEXT NOT NULL, message TEXT NOT NULL, event_time TIMESTAMPTZ NOT NULL, created_at TIMESTAMPTZ DEFAULT NOW())"""])

@app.get("/health")
def health(): return {"status":"ok", "service":"ingestion"}

@app.post("/api/logs", status_code=202)
def create_log(item: LogInput):
    event_id = str(uuid.uuid4())
    event_time = item.timestamp or datetime.now(timezone.utc)
    execute("INSERT INTO logs(id,source_ip,username,event_type,message,event_time) VALUES(%s,%s,%s,%s,%s,%s)",
            (event_id,item.source_ip,item.username,item.event_type,item.message,event_time))
    event = {"id":event_id,"source_ip":item.source_ip,"username":item.username,
             "event_type":item.event_type,"message":item.message,"timestamp":event_time.isoformat()}
    try:
        publish("log.received", event)
        published = True
    except Exception:
        logging.exception("Log stored but event publish failed")
        published = False
    return {"id":event_id,"stored":True,"published":published,"message":"Log accepted"}

@app.get("/api/logs")
def list_logs(limit: int=50):
    if not 1 <= limit <= 200: raise HTTPException(400,"limit must be 1..200")
    rows=fetch_all("SELECT * FROM logs ORDER BY created_at DESC LIMIT %s",(limit,))
    return [dict(r) for r in rows]
