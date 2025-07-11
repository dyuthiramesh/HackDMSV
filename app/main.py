from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from app.worker import generate_report_task
from app.state_manager import get_status
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OR use ["http://localhost:5500"] for stricter control
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/trigger_report")
def trigger_report(target: str, background_tasks: BackgroundTasks):
    report_id = str(uuid4())
    background_tasks.add_task(generate_report_task, target, report_id)
    return {"report_id": report_id}

@app.get("/status_report/{report_id}")
def status_report(report_id: str):
    status = get_status(report_id)

    if status == "not_found":
        raise HTTPException(status_code=404, detail="Report not found")

    elif status == "processing":
        return {"status": "processing"}

    elif status == "failed":
        return {"status": "failed", "message": "Report generation failed"}

    elif status == "done":
        file_path = f"data/{report_id}.pdf"
        if os.path.exists(file_path):
            return FileResponse(path=file_path, filename=f"{report_id}.pdf", media_type="application/pdf")
        else:
            return JSONResponse(status_code=500, content={"status": "done", "error": "PDF not found"})

    return {"status": "unknown"}
