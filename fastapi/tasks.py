import asyncio
import time
from typing import Any

from celery import states
from celery.utils.log import get_task_logger

from celery_app import celery_app
from services.recipe_parser import parse_recipe
from services.transcribe import transcribe_audio
from services.youtube import download_video
from utils import DATA_DIR, save_log, save_result

logger = get_task_logger(__name__)


def run_async(func, *args, **kwargs):
    """비동기 함수 실행을 Celery 동기 컨텍스트에서 처리."""
    return asyncio.run(func(*args, **kwargs))


@celery_app.task(bind=True, name="process_video")
def process_video_task(self, url: str) -> dict[str, Any]:
    """YouTube → 다운로드 → 자막/Whisper → LLM 파이프라인."""
    job_id = self.request.id
    job_dir = DATA_DIR / job_id
    job_dir.mkdir(exist_ok=True)

    timing: dict[str, float] = {}
    total_start = time.time()

    def update(progress: int, message: str, status: str = "processing", extra: dict | None = None):
        meta = {"status": status, "progress": progress, "message": message}
        if extra:
            meta.update(extra)
        logger.info(
            "[%s] state update | status=%s progress=%s message=%s extra=%s",
            job_id,
            meta.get("status"),
            meta.get("progress"),
            meta.get("message"),
            {k: v for k, v in meta.items() if k not in {"status", "progress", "message"}},
        )
        self.update_state(state="PROGRESS", meta=meta)
        return meta

    try:
        update(5, "영상 다운로드 중...")
        step_start = time.time()
        video_info = run_async(download_video, url, str(job_dir))
        timing["download"] = round(time.time() - step_start, 2)

        update(
            25,
            "음성 인식 준비 중...",
            extra={"video_info": {"video_id": video_info.get("video_id"), "title": video_info.get("title")}},
        )

        step_start = time.time()
        transcript = run_async(transcribe_audio, video_info["audio_path"])
        timing["stt"] = round(time.time() - step_start, 2)
        update(50, "레시피 분석 중...")

        step_start = time.time()
        recipe = run_async(parse_recipe, transcript)
        timing["parsing"] = round(time.time() - step_start, 2)
        update(70, "결과 정리 중...")

        timing["total"] = round(time.time() - total_start, 2)

        result = {
            "recipe": recipe,
            "video_info": video_info,
            "transcript": transcript,
            "timing": timing,
        }

        save_result(job_id, result)
        save_log("full", result, video_info.get("video_id"))
        self.update_state(state=states.SUCCESS, meta={"status": "completed", "progress": 100, "message": "완료"})
        return result
    except Exception as exc:
        logger.exception("Processing error for job %s", job_id)
        update(0, f"오류 발생: {exc}", status="failed")
        raise
