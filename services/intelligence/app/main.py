from fastapi import FastAPI
from shared.db import init_db, execute, fetch_one
app=FastAPI(title="SentinelMesh Threat Intelligence",version="1.0.0")
@app.on_event("startup")
def startup():
    init_db(["CREATE TABLE IF NOT EXISTS iocs (ip TEXT PRIMARY KEY, reputation INTEGER NOT NULL, category TEXT NOT NULL, notes TEXT NOT NULL)"])
    execute("INSERT INTO iocs(ip,reputation,category,notes) VALUES(%s,%s,%s,%s) ON CONFLICT(ip) DO NOTHING",("198.51.100.23",95,"simulated-malicious","Seeded demo IOC; documentation IP range"))
    execute("INSERT INTO iocs(ip,reputation,category,notes) VALUES(%s,%s,%s,%s) ON CONFLICT(ip) DO NOTHING",("203.0.113.77",75,"suspicious","Seeded demo IOC; documentation IP range"))
@app.get("/health")
def health(): return {"status":"ok","service":"intelligence"}
@app.get("/api/intelligence/ip/{ip}")
def lookup(ip:str):
    row=fetch_one("SELECT * FROM iocs WHERE ip=%s",(ip,))
    if row: return {**dict(row),"found":True}
    return {"ip":ip,"reputation":0,"category":"not_listed","notes":"No local IOC match","found":False}
