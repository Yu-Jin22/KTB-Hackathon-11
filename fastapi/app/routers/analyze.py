"""
영상 분석 라우터 모듈.

YouTube 영상 분석 및 레시피 추출 API를 제공합니다.
"""
import asyncio
import logging
import shutil
import time
import uuid
import httpx
import os
from datetime import datetime
from typing import Optional
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.config import DATA_DIR, JOB_EXPIRE_HOURS, MAX_JOBS
from app.exceptions import (
    RecipeParseError,
    TranscriptionError,
    YouTubeDownloadError,
)
from app.schemas.analyze import (
    AnalyzeRequest,
    AnalyzeResponse,
    JobStatusResponse,
)
from app.services.recipe_parser import parse_recipe
from app.services.transcribe import transcribe_audio
from app.services.youtube import download_video, extract_video_id

# =============================================================================
# 로깅 및 라우터 설정
# =============================================================================
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Analyze"])

# =============================================================================
# 상수
# =============================================================================
MIN_TRANSCRIPT_LENGTH = 20

DUMMY_RESULT = {
    "success": False,
    "elapsedTime": 0.0,
    "inputSegmentsCount": 0,
    "recipe": {
        "title": "두부찌개",
        "description": "간단하면서도 깊은 맛을 내는 두부찌개 레시피입니다. 초보자도 쉽게 따라할 수 있고, 얼큰하고 감칠맛이 좋아서 한 끼 식사로 잘 어울립니다.",
        "servings": "2",
        "total_time": "10분",
        "difficulty": "쉬움",
        "ingredients": [
            {"name": "양파", "amount": "1/2", "unit": "개", "note": "0.5cm 두께로 얇게 슬라이스"},
            {"name": "두부", "amount": "300", "unit": "g", "note": "1cm 두께로 정사각형 모양 썰기"},
            {"name": "물", "amount": "400", "unit": "ml", "note": ""},
            {"name": "고춧가루", "amount": "1", "unit": "큰술", "note": ""},
            {"name": "다진 마늘", "amount": "1", "unit": "작은술", "note": ""},
            {"name": "진간장", "amount": "1", "unit": "큰술", "note": ""},
            {"name": "멸치액젓", "amount": "1", "unit": "큰술", "note": ""},
            {"name": "올리고당", "amount": "1", "unit": "큰술", "note": "없으면 설탕으로 대체 가능"},
            {"name": "다시다", "amount": "1", "unit": "작은술", "note": ""},
            {"name": "대파", "amount": "1/2", "unit": "대", "note": "어슷썰기"},
            {"name": "청양고추", "amount": "1", "unit": "개", "note": "0.3cm 두께로 얇게 썰기"},
        ],
        "steps": [
            {
                "step_number": 1,
                "instruction": "양파 1/2개를 깨끗이 씻은 후, 도마 위에 올려 0.5cm 두께로 세로로 얇게 슬라이스해주세요.\n썰은 양파를 냄비 바닥에 골고루 펼쳐 깔아주세요.",
                "timestamp": 4.0,
                "duration": "1분",
                "details": "양파를 바닥에 깔면 찌개에 단맛과 감칠맛이 더해집니다.",
                "tips": "양파는 신선한 것으로 사용하세요. 너무 두껍게 썰면 익는데 시간이 더 걸릴 수 있어요.",
            },
            {
                "step_number": 2,
                "instruction": "두부 300g 한 모를 깨끗이 물로 헹군 후 물기를 살짝 제거하세요.\n도마 위에 올리고 1cm 두께의 정사각형 모양으로 적당히 썰어주세요.\n썰은 두부를 냄비에 양파 위에 고르게 올려주세요.",
                "timestamp": 4.0,
                "duration": "1분",
                "details": "두부를 너무 부드럽게 다루어 부서지지 않도록 주의하세요.",
                "tips": "물기가 너무 많으면 찌개가 묽어질 수 있으니 키친타월로 살짝 닦아주세요.",
            },
            {
                "step_number": 3,
                "instruction": "냄비에 물 400ml를 부어주세요.\n고춧가루 1큰술, 다진 마늘 1작은술, 진간장 1큰술, 멸치액젓 1큰술, 올리고당 1큰술, 다시다 1작은술을 모두 넣어주세요.\n중불로 맞추고 냄비의 내용물이 끓기 시작하면 약 5분간 끓여 주세요.",
                "timestamp": 8.0,
                "duration": "5분",
                "details": "이때 물이 끓으면서 양파와 두부에 양념 맛이 잘 배이도록 중불에서 조절하세요.\n끓는 동안 가끔 냄비 가장자리에서 올라오는 부글거림을 확인하세요.",
                "tips": "바글바글 강하게 끓이면 두부가 부서질 수 있으니 중불 유지가 중요합니다.",
            },
            {
                "step_number": 4,
                "instruction": "대파 1/2대를 씻어 청결히 하고 어슷하게 0.7cm 간격으로 썰어주세요.\n청양고추 1개도 깨끗이 씻은 뒤 0.3cm 두께로 얇게 썰어주세요.\n끓던 찌개에 대파와 청양고추를 넣고 약한 중불에서 2분간 더 끓여주세요.\n2분 후에 불을 끄고 바로 그릇에 담아 완성합니다.",
                "timestamp": 16.0,
                "duration": "2분",
                "details": "대파와 청양고추를 마지막에 넣으면 신선한 향과 알싸한 맛이 살아납니다.",
                "tips": "고추는 기호에 따라 조절하고, 너무 많이 넣으면 많이 맵기 때문에 초보자는 1개부터 시작하세요.",
            },
        ],
        "tips": [
            "찌개가 끓으면 뚜껑을 살짝 덮어 재료가 고루 익게 해주세요.",
            "멸치액젓 대신 까나리액젓을 사용해도 좋습니다.",
            "완성 후 식힌 뒤 냉장 보관 시 2일 이내에 드세요.",
            "두부찌개에 두부 대신 돼지고기나 참치를 넣어 변형할 수 있습니다.",
        ],
    },
    "video_info": {
        "video_id": "2KoUycJinko",
        "title": "여러가지 시도해보고 정착한 두부찌개 레시피",
        "duration": 20,
        "url": "https://www.youtube.com/shorts/2KoUycJinko",
    },
}

# =============================================================================
# 작업 관리자 클래스
# =============================================================================
class JobManager:
    """작업 상태 관리 클래스 (메모리 관리 포함)."""

    def __init__(
        self,
        max_jobs: int = MAX_JOBS,
        expire_hours: int = JOB_EXPIRE_HOURS
    ):
        self._jobs: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._max_jobs = max_jobs
        self._expire_hours = expire_hours
        self._lock = asyncio.Lock()

    def create_job(
        self,
        job_id: str,
        url: str,
        video_id: str
    ) -> Dict[str, Any]:
        """새 작업을 생성합니다."""
        job = {
            "job_id": job_id,
            "status": "pending",
            "progress": 0,
            "message": "대기 중...",
            "url": url,
            "video_id": video_id,
            "result": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        self._jobs[job_id] = job
        self._cleanup_old_jobs()
        return job

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """작업을 조회합니다."""
        return self._jobs.get(job_id)

    def update_job(self, job_id: str, **kwargs) -> None:
        """작업 상태를 업데이트합니다."""
        if job_id in self._jobs:
            self._jobs[job_id].update(kwargs)
            self._jobs[job_id]["updated_at"] = datetime.now()

    def delete_job(self, job_id: str) -> bool:
        """작업을 삭제합니다."""
        if job_id in self._jobs:
            del self._jobs[job_id]
            return True
        return False

    def cleanup_job_files(self, job_id: str) -> None:
        """작업 관련 파일을 삭제합니다."""
        job_dir = DATA_DIR / job_id
        if job_dir.exists():
            try:
                shutil.rmtree(job_dir)
                logger.debug(f"작업 파일 삭제: {job_dir}")
            except Exception as e:
                logger.warning(f"작업 파일 삭제 실패: {job_dir}, {e}")

    def get_stats(self) -> Dict[str, Any]:
        """작업 통계를 조회합니다."""
        status_counts: Dict[str, int] = {}
        for job in self._jobs.values():
            status = job.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_jobs": len(self._jobs),
            "max_jobs": self._max_jobs,
            "status_counts": status_counts
        }

    def _cleanup_old_jobs(self) -> None:
        """오래된 작업을 정리합니다."""
        expire_threshold = datetime.now() - timedelta(hours=self._expire_hours)

        expired_jobs = [
            job_id for job_id, job in self._jobs.items()
            if job.get("created_at", datetime.now()) < expire_threshold
        ]

        for job_id in expired_jobs:
            self.cleanup_job_files(job_id)
            del self._jobs[job_id]
            logger.info(f"만료된 작업 삭제: {job_id}")

        while len(self._jobs) > self._max_jobs:
            oldest_job_id = next(iter(self._jobs))
            self.cleanup_job_files(oldest_job_id)
            del self._jobs[oldest_job_id]
            logger.info(f"오래된 작업 삭제 (용량 초과): {oldest_job_id}")


# 전역 작업 관리자
job_manager = JobManager()


# =============================================================================
# 영상 처리 단계별 함수
# =============================================================================
async def _step_download(
    job_id: str,
    url: str,
    job_dir: Path
) -> Dict[str, Any]:
    """
    1단계: 영상 다운로드.

    Args:
        job_id: 작업 ID
        url: YouTube URL
        job_dir: 작업 디렉토리

    Returns:
        비디오 정보 딕셔너리

    Raises:
        Exception: 다운로드 실패 시
    """
    job_manager.update_job(
        job_id,
        status="processing",
        step="download",
        message="영상 다운로드 중...",
        progress=5
    )

    await push_progress_to_spring(
            job_id=job_id,
            status="processing",
            progress=5,
            step="download",
            message="📥 영상 다운로드 중..."
        )
    try:
        video_info = await download_video(url, str(job_dir))
    except YouTubeDownloadError as e:
        raise Exception(f"영상 다운로드 실패: {e}")

    job_manager.update_job(
        job_id,
        message="다운로드 완료!",
        progress=25,
        video_info=video_info
    )

    await push_progress_to_spring(
            job_id=job_id,
            status="processing",
            progress=25,
            step="download",
            message="✅ 다운로드 완료!"
        )
    
    return video_info


async def _step_extract_transcript(
    job_id: str,
    url: str,
    job_dir: Path,
    audio_path: str
) -> tuple[Dict[str, Any], str]:
    """
    2단계: 자막/STT 추출.

    YouTube 자막 먼저 시도, 없으면 Whisper STT 폴백.

    Args:
        job_id: 작업 ID
        url: YouTube URL
        job_dir: 작업 디렉토리
        audio_path: 오디오 파일 경로

    Returns:
        (transcript 딕셔너리, source 문자열) 튜플

    Raises:
        Exception: 텍스트 추출 실패 시
    """
    transcript = None
    transcript_source = None

    # # YouTube 자막 시도 (주석처리 - Whisper 성능 테스트용)
    # job_manager.update_job(
    #     job_id,
    #     step="subtitle",
    #     message="YouTube 자막 확인 중...",
    #     progress=28
    # )
    #
    # try:
    #     subtitle_info = await download_subtitles(url, str(job_dir))
    #     if subtitle_info:
    #         transcript = parse_json3_subtitles(subtitle_info["subtitle_path"])
    #         if transcript and transcript.get("full_text"):
    #             transcript_source = f"youtube_{subtitle_info['language']}"
    #             if subtitle_info["is_auto_generated"]:
    #                 transcript_source += "_auto"
    #             logger.info(
    #                 f"[{job_id[:8]}] YouTube 자막 사용: {transcript_source}"
    #             )
    # except (SubtitleError, Exception) as e:
    #     logger.warning(f"[{job_id[:8]}] YouTube 자막 처리 실패: {e}")

    # Whisper STT 사용 (자막 로직 비활성화)
    if True:  # 항상 Whisper 사용
        job_manager.update_job(
            job_id,
            step="stt",
            message="음성 인식 중... (Whisper AI)",
            progress=35
        )

        await push_progress_to_spring(
            job_id=job_id,
            status="processing",
            progress=35,
            step="download",
            message="🎤 음성 인식 중... (Whisper AI)"
        )
        
        try:
            transcript = await transcribe_audio(audio_path)
            transcript_source = "whisper"
            logger.info(f"[{job_id[:8]}] Whisper STT 사용")
        except TranscriptionError as e:
            raise Exception(f"음성 인식 실패: {e}")
    # else:  # 주석처리 - Whisper 성능 테스트용
    #     job_manager.update_job(
    #         job_id,
    #         message="YouTube 자막 사용!",
    #         progress=45
    #     )

    # 텍스트 유효성 최종 확인
    if not _is_valid_transcript(transcript):
        raise Exception(
            "영상에서 텍스트를 추출할 수 없습니다. "
            "음성이나 자막이 포함된 영상인지 확인해주세요."
        )

    job_manager.update_job(
        job_id,
        message="텍스트 추출 완료!",
        progress=50
    )

    await push_progress_to_spring(
            job_id=job_id,
            status="processing",
            progress=50,
            step="download",
            message="✅ 텍스트 추출 완료!"
        )
    return transcript, transcript_source


def _is_valid_transcript(transcript: Optional[Dict[str, Any]]) -> bool:
    """전사 결과가 유효한지 확인합니다."""
    if not transcript:
        return False
    full_text = transcript.get("full_text", "")
    return len(full_text) >= MIN_TRANSCRIPT_LENGTH


async def _step_parse_recipe(
    job_id: str,
    transcript: Dict[str, Any]
) -> Dict[str, Any]:
    """
    3단계: 레시피 파싱.

    Args:
        job_id: 작업 ID
        transcript: 전사 데이터

    Returns:
        레시피 딕셔너리

    Raises:
        Exception: 파싱 실패 시
    """
    job_manager.update_job(
        job_id,
        step="parsing",
        message="GPT-4o로 레시피 분석 중...",
        progress=55
    )

    await push_progress_to_spring(
            job_id=job_id,
            status="processing",
            progress=55,
            step="parsing",
            message="🤖 GPT-4o로 레시피 분석 중..."
        )
    
    try:
        recipe = await parse_recipe(transcript)
    except RecipeParseError as e:
        raise Exception(f"레시피 분석 실패: {e}")

    job_manager.update_job(
        job_id,
        message="레시피 분석 완료!",
        progress=90
    )

    await push_progress_to_spring(
            job_id=job_id,
            status="processing",
            progress=90,
            step="frames",
            message="✅ 레시피 분석 완료!"
        )
    return recipe


# =============================================================================
# 메인 처리 함수
# =============================================================================
async def process_dummy(job_id: str) -> None:
    job_manager.update_job(
        job_id,
        status="processing",
        step="dummy",
        message="더미 처리 중...",
        progress=10
    )

    await push_progress_to_spring(
        job_id=job_id,
        status="processing",
        progress=10,
        step="dummy",
        message="⏳ 더미 처리 중..."
    )

    await asyncio.sleep(5)

    job_manager.update_job(
        job_id,
        status="completed",
        step="done",
        message="더미 완료!",
        progress=100,
        result=DUMMY_RESULT
    )

    await push_progress_to_spring(
        job_id=job_id,
        status="completed",
        progress=100,
        step="done",
        message="🎉 더미 완료!"
    )

async def process_video(job_id: str, url: str) -> None:
    """
    비동기로 영상을 처리합니다.

    Args:
        job_id: 작업 ID
        url: YouTube URL
    """
    job_dir = DATA_DIR / job_id
    job_dir.mkdir(exist_ok=True)

    timing: Dict[str, Any] = {}
    total_start = time.time()

    try:
        # 1단계: 영상 다운로드
        step_start = time.time()
        video_info = await _step_download(job_id, url, job_dir)
        timing["download"] = round(time.time() - step_start, 2)
        logger.info(f"[{job_id[:8]}] 다운로드 완료: {timing['download']}초")

        # 2단계: 자막/STT 추출
        step_start = time.time()
        transcript, transcript_source = await _step_extract_transcript(
            job_id, url, job_dir, video_info["audio_path"]
        )
        timing["transcript"] = round(time.time() - step_start, 2)
        timing["transcript_source"] = transcript_source
        logger.info(
            f"[{job_id[:8]}] 텍스트 추출 완료: {timing['transcript']}초 "
            f"(소스: {transcript_source})"
        )

        # 3단계: 레시피 파싱
        step_start = time.time()
        recipe = await _step_parse_recipe(job_id, transcript)
        timing["parsing"] = round(time.time() - step_start, 2)
        logger.info(f"[{job_id[:8]}] 레시피 파싱 완료: {timing['parsing']}초")

        # 총 소요 시간
        timing["total"] = round(time.time() - total_start, 2)
        logger.info(f"[{job_id[:8]}] === 전체 완료: {timing['total']}초 ===")

        # 결과 저장
        job_manager.update_job(
            job_id,
            step="done",
            message="레시피 추출 완료!",
            progress=100,
            status="completed",
            result={
                "recipe": recipe,
                "video_info": video_info,
                "transcript": transcript,
                "timing": timing
            }
        )

        await push_progress_to_spring(
            job_id=job_id,
            status="completed",
            progress=100,
            step="done",
            message="🎉 레시피 추출 완료!"
        )
    except Exception as e:
        error_message = str(e)
        logger.error(f"[{job_id[:8]}] 처리 오류: {error_message}")

        job_manager.update_job(
            job_id,
            status="failed",
            message=f"오류 발생: {error_message}",
            progress=0
        )

        await push_progress_to_spring(
            job_id=job_id,
            status="failed",
            progress=0,
            step="done",
            message=f"오류 발생: {error_message}"
        )

# =============================================================================
# API 엔드포인트
# =============================================================================
@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_video(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks
) -> AnalyzeResponse:
    """
    YouTube URL을 받아 분석을 시작합니다.

    Args:
        request: 분석 요청 (YouTube URL 포함)
        background_tasks: 백그라운드 작업 큐

    Returns:
        작업 ID와 메시지
    """
    url = str(request.url).strip()

    if not url:
        raise HTTPException(
            status_code=400,
            detail="URL이 제공되지 않았습니다."
        )

    video_id = extract_video_id(url)
    if not video_id:
        raise HTTPException(
            status_code=400,
            detail="유효하지 않은 YouTube URL입니다."
        )

    job_id = str(uuid.uuid4())

    job_manager.create_job(job_id, url, video_id)
    logger.info(f"새 작업 생성: {job_id[:8]}, video_id={video_id}")

    background_tasks.add_task(process_dummy, job_id)

    return AnalyzeResponse(job_id=job_id, message="분석을 시작합니다.")


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    작업 상태를 조회합니다.

    Args:
        job_id: 작업 ID

    Returns:
        작업 상태 정보
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="작업을 찾을 수 없습니다."
        )

    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        message=job["message"],
        video_id=job.get("video_id")
    )


@router.get("/result/{job_id}")
async def get_result(job_id: str) -> Dict[str, Any]:
    """
    분석 결과를 조회합니다.

    Args:
        job_id: 작업 ID

    Returns:
        분석 결과 (레시피, 비디오 정보 등)
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="작업을 찾을 수 없습니다."
        )

    if job["status"] == "failed":
        raise HTTPException(
            status_code=400,
            detail=job.get("message", "작업이 실패했습니다.")
        )

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail="아직 처리가 완료되지 않았습니다."
        )

    return job["result"]


@router.delete("/job/{job_id}")
async def delete_job(job_id: str) -> Dict[str, str]:
    """
    작업을 삭제합니다.

    Args:
        job_id: 작업 ID

    Returns:
        삭제 결과
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="작업을 찾을 수 없습니다."
        )

    job_manager.cleanup_job_files(job_id)
    job_manager.delete_job(job_id)
    logger.info(f"작업 삭제됨: {job_id[:8]}")

    return {"message": "작업이 삭제되었습니다.", "job_id": job_id}


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """
    작업 통계를 조회합니다.

    Returns:
        작업 통계 정보
    """
    return job_manager.get_stats()

# =============================================================================
# Spring BE 콜백
# =============================================================================


# ✅ Spring 콜백 대상 (상수로 고정)
SPRING_BASE = os.getenv("SPRING_BASE")
PROGRESS_WEBHOOK_PATH = "/api/internal/jobs/{jobId}/progress"
WEBHOOK_TIMEOUT = 5.0

async def push_progress_to_spring(
    *,
    job_id: str,
    status: str,
    progress: int,
    step: str,
    message: str,
) -> None:
    """
    FastAPI -> Spring 내부 progress 콜백 전송
    - 실패해도 작업은 계속 진행 (로그만)
    - Spring DTO 기준: jobId / videoId
    """
    payload = {
        "status": status,              # pending|processing|completed|failed
        "progress": int(progress),     # 0~100
        "step": step,
        "message": message
    }

    try:
        async with httpx.AsyncClient(timeout=WEBHOOK_TIMEOUT) as client:
            await client.post(
                f"{SPRING_BASE}{PROGRESS_WEBHOOK_PATH.format(jobId=job_id)}",
                json=payload,
            )
    except Exception as e:
        # 콜백 실패가 job 처리 실패로 이어지면 안 됨
        print(f"[push_progress_to_spring] failed: {e}")
