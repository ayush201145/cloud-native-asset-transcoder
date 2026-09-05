from fastapi import FastAPI, UploadFile, File, BackgroundTasks
import os
import uuid
from transcoder.ffmpeg_pipeline import HLSVideoTranscoder

app = FastAPI(
    title="Cloud-Native Asset Transcoding Pipeline API",
    description="Media portal where high-resolution video uploads trigger background workers for adaptive HLS stream encoding."
)

UPLOAD_DIR = "./storage/uploads"
OUTPUT_DIR = "./storage/hls"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    job_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    job_output_dir = os.path.join(OUTPUT_DIR, job_id)
    
    # Process transcoding in background task queue
    background_tasks.add_task(HLSVideoTranscoder.transcode_to_hls, file_path, job_output_dir)

    return {
        "job_id": job_id,
        "filename": file.filename,
        "status": "QUEUED",
        "hls_stream_url": f"/api/streams/{job_id}/master.m3u8"
    }

@app.get("/api/jobs/{job_id}")
def get_job_status(job_id: str):
    job_path = os.path.join(OUTPUT_DIR, job_id, "master.m3u8")
    if os.path.exists(job_path):
        return {"job_id": job_id, "status": "READY", "stream_url": f"/api/streams/{job_id}/master.m3u8"}
    return {"job_id": job_id, "status": "PROCESSING"}
