from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

app = FastAPI(title="Latency Analytics POST Endpoint")

# Enable CORS for all origins (necessary for browser POST requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow requests from any origin
    allow_methods=["POST"],     # Only allow POST
    allow_headers=["*"]
)

@app.post("/")
async def latency_metrics(request: Request):
    """
    Accepts JSON POST:
    {
        "regions": [...],
        "threshold_ms": 180
    }

    Returns per-region metrics:
    avg_latency, p95_latency, avg_uptime, breaches
    """
    data = await request.json()
    regions = data.get("regions", [])
    threshold = data.get("threshold_ms", 180)

    # Example telemetry data
    telemetry = {
        "emea": [{"latency": 100, "uptime": 99}, {"latency": 200, "uptime": 98}],
        "amer": [{"latency": 150, "uptime": 100}, {"latency": 160, "uptime": 99}],
    }

    response = {}
    for region in regions:
        records = telemetry.get(region, [])
        if not records:
            response[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue

        latencies = [r["latency"] for r in records]
        uptimes = [r["uptime"] for r in records]
        breaches = sum(1 for l in latencies if l > threshold)

        response[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": int(breaches)
        }

    return response
