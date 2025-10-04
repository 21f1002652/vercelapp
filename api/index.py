from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import numpy as np

app = FastAPI(title="Latency Analytics POST Endpoint")

# Fake telemetry data
telemetry = {
    "emea": [{"latency": 100, "uptime": 99}, {"latency": 200, "uptime": 98}],
    "amer": [{"latency": 150, "uptime": 100}, {"latency": 160, "uptime": 99}],
}

# CORS headers
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "*"
}

# OPTIONS route for preflight
@app.options("/")
async def preflight():
    return JSONResponse(content={"status": "ok"}, headers=CORS_HEADERS)

# POST endpoint
@app.post("/")
async def latency_metrics(request: Request):
    data = await request.json()
    regions = data.get("regions", [])
    threshold = data.get("threshold_ms", 180)

    response_data = {}
    for region in regions:
        records = telemetry.get(region, [])
        if not records:
            response_data[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue

        latencies = [r["latency"] for r in records]
        uptimes = [r["uptime"] for r in records]
        breaches = sum(1 for l in latencies if l > threshold)

        response_data[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": int(breaches)
        }

    return JSONResponse(content=response_data, headers=CORS_HEADERS)
