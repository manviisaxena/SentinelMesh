import os, logging, threading
from fastapi import FastAPI
import httpx, pybreaker
from shared.db import init_db, execute, fetch_all, fetch_one
from shared.messaging import publish, start_consumer
from .rules import score_event
logging.basicConfig(level=os.getenv("LOG_LEVEL","INFO"))
app=FastAPI(title="SentinelMesh Threat Detection",version="1.0.0")
INTELLIGENCE_URL=os.getenv("INTELLIGENCE_URL","http://intelligence:8003")
breaker=pybreaker.CircuitBreaker(fail_max=3, reset_timeout=10, name="intelligence")

def enrich(ip):
    @breaker
    def call():
        response=httpx.get(f"{INTELLIGENCE_URL}/api/intelligence/ip/{ip}",timeout=2.0)
        response.raise_for_status(); return response.json()
    try:
        result=call()
        return result.get("reputation",0),"available",result.get("category","unknown")
    except pybreaker.CircuitBreakerError:
        logging.warning("circuit_open: using unknown reputation fallback")
        return 0,"unavailable","unknown"
    except Exception:
        logging.exception("intelligence unavailable; safe fallback is unknown")
        return 0,"unavailable","unknown"

def process_event(event):
    ip=event.get("source_ip","unknown")
    if event.get("event_type")=="login_failed":
        execute("INSERT INTO login_attempts(source_ip,event_id) VALUES(%s,%s) ON CONFLICT(event_id) DO NOTHING",(ip,event.get("id")))
        recent=fetch_one("SELECT COUNT(*) AS n FROM login_attempts WHERE source_ip=%s AND created_at > NOW() - INTERVAL '10 minutes'",(ip,))
        count=(recent or {}).get("n",1)
    else:
        count=1
    reputation,status,category=enrich(ip)
    score,severity,reasons=score_event(event,count,reputation)
    row=execute("INSERT INTO threats(source_ip,event_id,username,event_type,risk_score,severity,reasons,enrichment_status,ip_category) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
        (ip,event.get("id"),event.get("username","unknown"),event.get("event_type","other"),score,severity,",".join(reasons),status,category),True)
    if score>=35:
        publish("threat.detected",{"id":row["id"],"source_ip":ip,"risk_score":score,"severity":severity,"reasons":reasons,"username":event.get("username","unknown")})

@app.on_event("startup")
def startup():
    init_db(["""CREATE TABLE IF NOT EXISTS threats (id BIGSERIAL PRIMARY KEY, source_ip TEXT NOT NULL, event_id TEXT, username TEXT, event_type TEXT, risk_score INTEGER NOT NULL, severity TEXT NOT NULL, reasons TEXT NOT NULL, enrichment_status TEXT NOT NULL, ip_category TEXT NOT NULL, created_at TIMESTAMPTZ DEFAULT NOW())""",
             """CREATE TABLE IF NOT EXISTS login_attempts (id BIGSERIAL PRIMARY KEY, source_ip TEXT NOT NULL, event_id TEXT UNIQUE, created_at TIMESTAMPTZ DEFAULT NOW())"""])
    start_consumer("detection.log.received","log.received",process_event)
@app.get("/health")
def health(): return {"status":"ok","service":"detection","circuit_breaker":breaker.current_state}
@app.get("/api/threats")
def threats(limit:int=50):
    rows=fetch_all("SELECT * FROM threats ORDER BY created_at DESC LIMIT %s",(max(1,min(limit,200)),))
    return [dict(r) for r in rows]
