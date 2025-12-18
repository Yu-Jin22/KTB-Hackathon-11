import json
from datetime import datetime
from pathlib import Path
from typing import Any

# 공용 데이터/로그 경로
DATA_DIR = Path("data")
LOG_DIR = DATA_DIR / "logs"

# 기본 디렉터리 보장
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)


def save_log(log_type: str, data: dict, video_id: str | None = None) -> str:
    """JSON 형태의 로그를 파일로 저장한다."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = f"{video_id}_" if video_id else ""
    filename = f"{prefix}{log_type}_{timestamp}.json"
    filepath = LOG_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return str(filepath)


def save_result(job_id: str, data: dict[str, Any]) -> str:
    """작업 결과를 디스크에 저장한다."""
    job_dir = DATA_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    filepath = job_dir / "result.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return str(filepath)


def load_result(job_id: str) -> dict[str, Any] | None:
    """디스크에 저장된 작업 결과를 불러온다."""
    filepath = DATA_DIR / job_id / "result.json"
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None
