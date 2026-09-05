import os
from celery import Celery
from transcoder.ffmpeg_pipeline import HLSVideoTranscoder

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("transcoder_worker", broker=REDIS_URL, backend=REDIS_URL)

@celery_app.task(name="tasks.transcode_video")
def transcode_video_task(job_id: str, input_path: str, output_dir: str):
    print(f"Processing background transcoding job [{job_id}]...")
    result = HLSVideoTranscoder.transcode_to_hls(input_path, output_dir)
    return {"job_id": job_id, "result": result}
