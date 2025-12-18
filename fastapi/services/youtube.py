import os
import re
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional, List

import yt_dlp

logger = logging.getLogger(__name__)


class YouTubeDownloadError(Exception):
    """YouTube 다운로드 중 발생하는 에러"""
    pass


class VideoNotFoundError(YouTubeDownloadError):
    """영상을 찾을 수 없는 경우"""
    pass


class VideoUnavailableError(YouTubeDownloadError):
    """영상이 비공개이거나 삭제된 경우"""
    pass


# 지원하는 비디오 확장자
SUPPORTED_VIDEO_EXTENSIONS = ['mp4', 'webm', 'mkv', 'mov', 'avi']

# 최대 영상 길이 (초) - 쇼츠는 보통 60초 이하
MAX_VIDEO_DURATION = 180  # 3분


def _create_progress_hook(label: str):
    """다운로드 진행률 로깅용 hook (10% 단위로만 출력)"""
    last_logged = [0]  # closure로 상태 유지

    def hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percent = int(downloaded / total * 100)
                # 10% 단위로만 로그 출력
                if percent >= last_logged[0] + 10:
                    last_logged[0] = (percent // 10) * 10
                    speed = d.get('speed')
                    speed_str = f"{speed / 1024 / 1024:.1f}MB/s" if speed else "..."
                    logger.info(f"[{label}] 다운로드 {percent}% ({speed_str})")
        elif d['status'] == 'finished':
            logger.info(f"[{label}] 다운로드 완료")

    return hook


def extract_video_id(url: str) -> Optional[str]:
    """
    YouTube URL에서 video ID 추출

    Args:
        url: YouTube URL

    Returns:
        str | None: 비디오 ID 또는 None
    """
    if not url:
        return None

    patterns = [
        r'(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]+)',
        r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]+)',
        r'(?:youtu\.be\/)([a-zA-Z0-9_-]+)',
        r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


async def download_video(url: str, output_dir: str) -> dict:
    """
    YouTube 쇼츠 영상과 오디오를 다운로드합니다.

    Args:
        url: YouTube URL
        output_dir: 출력 디렉토리

    Returns:
        dict: {
            'video_path': str,
            'audio_path': str,
            'video_id': str,
            'title': str,
            'duration': float,
            'url': str
        }

    Raises:
        YouTubeDownloadError: 다운로드 실패 시
        VideoNotFoundError: 영상을 찾을 수 없는 경우
        VideoUnavailableError: 영상이 비공개/삭제된 경우
    """
    # URL 검증
    video_id = extract_video_id(url)
    if not video_id:
        raise VideoNotFoundError(f"유효하지 않은 YouTube URL입니다: {url}")

    # 출력 디렉토리 생성
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    loop = asyncio.get_event_loop()

    # 1. 영상 정보 가져오기
    logger.info(f"영상 정보 조회 중: {video_id}")

    ydl_opts_info = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }

    try:
        def get_info():
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                return ydl.extract_info(url, download=False)

        info = await loop.run_in_executor(None, get_info)

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e).lower()
        if 'private' in error_msg or 'unavailable' in error_msg:
            raise VideoUnavailableError(f"영상이 비공개이거나 삭제되었습니다: {video_id}")
        elif 'not found' in error_msg or '404' in error_msg:
            raise VideoNotFoundError(f"영상을 찾을 수 없습니다: {video_id}")
        else:
            raise YouTubeDownloadError(f"영상 정보 조회 실패: {e}")

    except Exception as e:
        raise YouTubeDownloadError(f"영상 정보 조회 중 오류: {e}")

    if not info:
        raise VideoNotFoundError(f"영상 정보를 가져올 수 없습니다: {video_id}")

    # 정보 추출
    actual_video_id = info.get('id', video_id)
    title = info.get('title', 'untitled')
    duration = info.get('duration', 0)

    logger.info(f"영상 정보: {title} ({duration}초)")

    # 영상 길이 검증
    if duration and duration > MAX_VIDEO_DURATION:
        logger.warning(f"영상이 너무 깁니다: {duration}초 (최대 {MAX_VIDEO_DURATION}초)")
        # 경고만 하고 계속 진행 (쇼츠가 아닐 수도 있음)

    video_path = os.path.join(output_dir, f"{actual_video_id}.mp4")
    audio_path = os.path.join(output_dir, f"{actual_video_id}.mp3")

    # 2. 영상 다운로드
    logger.info(f"영상 다운로드 중: {actual_video_id}")

    ydl_opts_video = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, f"{actual_video_id}.%(ext)s"),
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'progress_hooks': [_create_progress_hook('영상')],
        'socket_timeout': 30,
        'retries': 3,
    }

    try:
        def download_vid():
            with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                ydl.download([url])

        await loop.run_in_executor(None, download_vid)

    except yt_dlp.utils.DownloadError as e:
        raise YouTubeDownloadError(f"영상 다운로드 실패: {e}")
    except Exception as e:
        raise YouTubeDownloadError(f"영상 다운로드 중 오류: {e}")

    # 3. 오디오 추출
    logger.info(f"오디오 추출 중: {actual_video_id}")

    ydl_opts_audio = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, f"{actual_video_id}.%(ext)s"),
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'progress_hooks': [_create_progress_hook('오디오')],
        'socket_timeout': 30,
        'retries': 3,
    }

    try:
        def download_aud():
            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                ydl.download([url])

        await loop.run_in_executor(None, download_aud)

    except yt_dlp.utils.DownloadError as e:
        raise YouTubeDownloadError(f"오디오 추출 실패: {e}")
    except Exception as e:
        raise YouTubeDownloadError(f"오디오 추출 중 오류: {e}")

    # 4. 다운로드된 파일 확인
    actual_video = None
    for ext in SUPPORTED_VIDEO_EXTENSIONS:
        check_path = os.path.join(output_dir, f"{actual_video_id}.{ext}")
        if os.path.exists(check_path) and os.path.getsize(check_path) > 0:
            actual_video = check_path
            break

    if not actual_video:
        raise YouTubeDownloadError(f"다운로드된 비디오 파일을 찾을 수 없습니다: {actual_video_id}")

    if not os.path.exists(audio_path):
        raise YouTubeDownloadError(f"추출된 오디오 파일을 찾을 수 없습니다: {audio_path}")

    if os.path.getsize(audio_path) == 0:
        raise YouTubeDownloadError(f"오디오 파일이 비어있습니다: {audio_path}")

    logger.info(f"다운로드 완료: video={actual_video}, audio={audio_path}")

    return {
        'video_path': actual_video,
        'audio_path': audio_path,
        'video_id': actual_video_id,
        'title': title,
        'duration': duration,
        'url': url
    }


async def get_video_info(url: str) -> Optional[dict]:
    """
    영상 정보만 조회 (다운로드 없이)

    Args:
        url: YouTube URL

    Returns:
        dict | None: 영상 정보 또는 None
    """
    video_id = extract_video_id(url)
    if not video_id:
        return None

    loop = asyncio.get_event_loop()

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }

    try:
        def get_info():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)

        info = await loop.run_in_executor(None, get_info)

        if info:
            return {
                'video_id': info.get('id'),
                'title': info.get('title'),
                'duration': info.get('duration'),
                'thumbnail': info.get('thumbnail'),
                'channel': info.get('channel'),
                'view_count': info.get('view_count'),
            }

    except Exception as e:
        logger.error(f"영상 정보 조회 실패: {e}")

    return None


# 자막 우선순위 (한국어 우선)
SUBTITLE_LANG_PRIORITY = ['ko', 'en', 'ja']


async def download_subtitles(url: str, output_dir: str) -> Optional[dict]:
    """
    YouTube 영상의 자막을 다운로드합니다.
    자동 생성 자막(auto-generated)을 포함하여 시도합니다.

    Args:
        url: YouTube URL
        output_dir: 출력 디렉토리

    Returns:
        dict | None: {
            'subtitle_path': str,
            'language': str,
            'is_auto_generated': bool
        } 또는 자막이 없으면 None
    """
    video_id = extract_video_id(url)
    if not video_id:
        return None

    loop = asyncio.get_event_loop()
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 먼저 사용 가능한 자막 목록 확인
    ydl_opts_info = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }

    try:
        def get_info():
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                return ydl.extract_info(url, download=False)

        info = await loop.run_in_executor(None, get_info)

    except Exception as e:
        logger.warning(f"자막 정보 조회 실패: {e}")
        return None

    if not info:
        return None

    # 수동 자막과 자동 생성 자막 확인
    subtitles = info.get('subtitles', {})
    auto_captions = info.get('automatic_captions', {})

    # 우선순위에 따라 언어 선택
    selected_lang = None
    is_auto = False

    # 1. 수동 자막 먼저 확인 (품질이 더 좋음)
    for lang in SUBTITLE_LANG_PRIORITY:
        if lang in subtitles:
            selected_lang = lang
            is_auto = False
            logger.info(f"수동 자막 발견: {lang}")
            break

    # 2. 수동 자막 없으면 자동 생성 자막 확인
    if not selected_lang:
        for lang in SUBTITLE_LANG_PRIORITY:
            if lang in auto_captions:
                selected_lang = lang
                is_auto = True
                logger.info(f"자동 생성 자막 발견: {lang}")
                break

    # 3. 우선순위 언어 없으면 원본 언어 사용
    if not selected_lang:
        # 자동 자막에서 첫 번째 사용 가능한 언어
        if auto_captions:
            selected_lang = next(iter(auto_captions.keys()))
            is_auto = True
            logger.info(f"기본 자동 자막 사용: {selected_lang}")
        elif subtitles:
            selected_lang = next(iter(subtitles.keys()))
            is_auto = False
            logger.info(f"기본 수동 자막 사용: {selected_lang}")

    if not selected_lang:
        logger.info("사용 가능한 자막 없음")
        return None

    # 자막 다운로드
    subtitle_path = os.path.join(output_dir, f"{video_id}.{selected_lang}.json3")

    ydl_opts_sub = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'writesubtitles': not is_auto,
        'writeautomaticsub': is_auto,
        'subtitleslangs': [selected_lang],
        'subtitlesformat': 'json3',
        'outtmpl': os.path.join(output_dir, f"{video_id}"),
    }

    try:
        def download_sub():
            with yt_dlp.YoutubeDL(ydl_opts_sub) as ydl:
                ydl.download([url])

        await loop.run_in_executor(None, download_sub)

    except Exception as e:
        logger.warning(f"자막 다운로드 실패: {e}")
        return None

    # 다운로드된 파일 확인
    if not os.path.exists(subtitle_path):
        logger.warning(f"자막 파일을 찾을 수 없음: {subtitle_path}")
        return None

    logger.info(f"자막 다운로드 완료: {subtitle_path}")

    return {
        'subtitle_path': subtitle_path,
        'language': selected_lang,
        'is_auto_generated': is_auto
    }


def parse_json3_subtitles(subtitle_path: str) -> Optional[dict]:
    """
    JSON3 형식의 자막 파일을 파싱하여 transcript 형식으로 변환합니다.

    Args:
        subtitle_path: JSON3 자막 파일 경로

    Returns:
        dict | None: {
            'full_text': str,
            'segments': [{'start': float, 'end': float, 'text': str}]
        }
    """
    try:
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"자막 파일 읽기 실패: {e}")
        return None

    events = data.get('events', [])
    if not events:
        logger.warning("자막 이벤트가 없습니다")
        return None

    segments: List[dict] = []
    full_text_parts: List[str] = []

    for event in events:
        # 텍스트 세그먼트가 있는 이벤트만 처리
        segs = event.get('segs', [])
        if not segs:
            continue

        # 시작 시간 (밀리초 → 초)
        start_ms = event.get('tStartMs', 0)
        duration_ms = event.get('dDurationMs', 0)
        start_sec = start_ms / 1000.0
        end_sec = (start_ms + duration_ms) / 1000.0

        # 텍스트 조합
        text_parts = []
        for seg in segs:
            utf8_text = seg.get('utf8', '')
            if utf8_text and utf8_text.strip() and utf8_text != '\n':
                text_parts.append(utf8_text)

        if text_parts:
            text = ''.join(text_parts).strip()
            if text and text != '[Music]' and text != '[음악]':
                segments.append({
                    'start': round(start_sec, 2),
                    'end': round(end_sec, 2),
                    'text': text
                })
                full_text_parts.append(text)

    if not segments:
        logger.warning("파싱된 자막 세그먼트가 없습니다")
        return None

    # 중복 제거 및 정리
    cleaned_segments = []
    prev_text = ""
    for seg in segments:
        if seg['text'] != prev_text:
            cleaned_segments.append(seg)
            prev_text = seg['text']

    full_text = ' '.join([seg['text'] for seg in cleaned_segments])

    logger.info(f"자막 파싱 완료: {len(cleaned_segments)}개 세그먼트, {len(full_text)}자")

    return {
        'full_text': full_text,
        'segments': cleaned_segments
    }
