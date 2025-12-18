import os
import time
from typing import Optional
from contextlib import asynccontextmanager

from celery import states
from celery.result import AsyncResult
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from dotenv import load_dotenv

from celery_app import celery_app
from tasks import process_video_task
from services.youtube import download_video, extract_video_id
from services.transcribe import transcribe_audio
from services.recipe_parser import parse_recipe, get_step_timestamps

from services.export import generate_markdown, generate_pdf
from utils import DATA_DIR, save_log, load_result

load_dotenv()

class AnalyzeRequest(BaseModel):
    url: str


class JobStatus(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    message: str
    result: Optional[dict] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    DATA_DIR.mkdir(exist_ok=True)
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title="쇼츠 레시피 정리기",
    description="YouTube 쇼츠에서 레시피를 추출하고 정리합니다",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/analyze")
async def analyze_video(request: AnalyzeRequest):
    """YouTube URL을 받아 분석을 시작합니다."""
    url = request.url

    # URL 유효성 검사
    video_id = extract_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="유효하지 않은 YouTube URL입니다.")

    task = process_video_task.delay(url)

    return {"job_id": task.id, "video_id": video_id, "message": "Celery 작업을 시작했습니다."}


@app.get("/api/status/{job_id}")
async def get_job_status(job_id: str):
    """작업 상태를 조회합니다."""
    task = AsyncResult(job_id, app=celery_app)
    meta = task.info if isinstance(task.info, dict) else {}
    cached_result = load_result(job_id)

    # Celery -> API 상태 매핑
    if task.state == states.PENDING:
        status = "pending"
        progress = 0
        message = "대기 중..."
    elif task.state in (states.STARTED, "PROGRESS"):
        status = meta.get("status", "processing")
        progress = meta.get("progress", 0)
        message = meta.get("message", "처리 중...")
    elif task.state == states.SUCCESS:
        status = "completed"
        progress = 100
        message = "완료"
    elif task.state == states.FAILURE:
        status = "failed"
        progress = 0
        message = f"오류: {str(task.info)}"
    else:
        status = task.state.lower()
        progress = meta.get("progress", 0)
        message = meta.get("message", task.state)

    video_id = None
    if isinstance(meta.get("video_info"), dict):
        video_id = meta["video_info"].get("video_id")
    elif cached_result:
        video_id = cached_result.get("video_info", {}).get("video_id")

    return {
        "job_id": job_id,
        "status": status,
        "progress": progress,
        "message": message,
        "video_id": video_id,
    }


@app.get("/api/result/{job_id}")
async def get_result(job_id: str):
    """분석 결과를 조회합니다."""
    task = AsyncResult(job_id, app=celery_app)

    if task.state != states.SUCCESS:
        cached = load_result(job_id)
        if cached:
            return cached
        raise HTTPException(status_code=400, detail="아직 처리가 완료되지 않았습니다.")

    result_data = load_result(job_id) or task.result
    if not result_data:
        raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다.")

    return result_data


@app.get("/api/export/{job_id}")
async def export_recipe(job_id: str, format: str = "markdown"):
    """레시피를 내보냅니다."""
    task = AsyncResult(job_id, app=celery_app)
    result = load_result(job_id) or (task.result if task.state == states.SUCCESS else None)
    if not result:
        raise HTTPException(status_code=400, detail="아직 처리가 완료되지 않았습니다.")

    recipe = result["recipe"]
    frames = result["frames"]

    job_dir = DATA_DIR / job_id
    frames_dir = job_dir / "frames"

    if format == "markdown":
        md_content = generate_markdown(recipe, frames, include_images=False)
        return Response(
            content=md_content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f'attachment; filename="{recipe.get("title", "recipe")}.md"'
            }
        )

    elif format == "pdf":
        pdf_path = job_dir / "recipe.pdf"
        success = generate_pdf(recipe, frames, str(pdf_path), str(frames_dir))

        if not success or not pdf_path.exists():
            raise HTTPException(status_code=500, detail="PDF 생성에 실패했습니다.")

        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=f"{recipe.get('title', 'recipe')}.pdf"
        )

    else:
        raise HTTPException(status_code=400, detail="지원하지 않는 형식입니다. (markdown, pdf)")

'''
@app.get("/api/frames/{job_id}/{filename}")
async def get_frame(job_id: str, filename: str):
    """캡처된 프레임 이미지를 반환합니다."""
    frame_path = DATA_DIR / job_id / "frames" / filename

    if not frame_path.exists():
        raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")

    return FileResponse(str(frame_path), media_type="image/jpeg")
'''

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy"}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
