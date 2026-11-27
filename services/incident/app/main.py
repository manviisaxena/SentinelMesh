from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from shared.db import init_db, execute, fetch_all
from shared.messaging import start_consumer
app=FastAPI(title="SentinelMesh Incident Management",version="1.0.0")
def create_incident(event):
    execute("INSERT INTO incidents(threat_id,source_ip,risk_score,severity,reasons,username,status) VALUES(%s,%s,%s,%s,%s,%s,'open') ON CONFLICT(threat_id) DO NOTHING",
        (event.get("id"),event.get("source_ip"),event.get("risk_score",0),event.get("severity","low"),",".join(event.get("reasons",[])),event.get("username","unknown")))
@app.on_event("startup")
def startup():
    init_db(["""CREATE TABLE IF NOT EXISTS incidents (id BIGSERIAL PRIMARY KEY, threat_id BIGINT UNIQUE NOT NULL, source_ip TEXT NOT NULL, risk_score INTEGER NOT NULL, severity TEXT NOT NULL, reasons TEXT NOT NULL, username TEXT, status TEXT NOT NULL DEFAULT 'open', created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW())"""])
    start_consumer("incident.threat.detected","threat.detected",create_incident)
@app.get("/health")
def health(): return {"status":"ok","service":"incident"}
@app.get("/api/incidents")
def incidents(limit:int=50):
    return [dict(r) for r in fetch_all("SELECT * FROM incidents ORDER BY created_at DESC LIMIT %s",(max(1,min(limit,200)),))]
class StatusUpdate(BaseModel): status:str=Field(pattern="^(open|acknowledged|resolved)$")
@app.patch("/api/incidents/{incident_id}/status")
def update_status(incident_id:int, body:StatusUpdate):
    row=execute("UPDATE incidents SET status=%s,updated_at=NOW() WHERE id=%s RETURNING *",(body.status,incident_id),True)
    if not row: raise HTTPException(404,"Incident not found")
    return dict(row)
