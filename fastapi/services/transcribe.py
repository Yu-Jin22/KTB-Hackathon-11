import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

from utils import save_log

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Whisper 힌트 프롬프트 - 한국어 요리 용어
COOKING_PROMPT = """한국어 요리 레시피 영상입니다.
재료: 양파, 대파, 파채, 당근, 감자, 마늘, 생강, 고추, 청양고추, 홍고추, 깻잎, 부추, 시금치, 콩나물, 숙주, 버섯, 표고버섯, 새송이버섯, 팽이버섯, 애호박, 오이, 무, 배추, 양배추, 두부, 계란, 달걀, 소고기, 돼지고기, 삼겹살, 닭고기, 닭가슴살, 참치, 참치캔, 새우, 오징어, 조개, 햄, 스팸, 베이컨, 소시지, 어묵
양념: 간장, 진간장, 국간장, 양조간장, 고추장, 된장, 쌈장, 고춧가루, 소금, 설탕, 식초, 참기름, 들기름, 식용유, 올리브유, 다진마늘, 다진생강, 후추, 맛술, 미림, 굴소스, 액젓, 까나리액젓, 멸치액젓, 매실청, 물엿, 올리고당, 케첩, 마요네즈, 머스타드
조리법: 썰다, 다지다, 채썰다, 송송 썰다, 어슷썰다, 깍둑썰기, 볶다, 굽다, 찌다, 삶다, 끓이다, 튀기다, 조리다, 무치다, 버무리다, 재우다, 절이다, 데치다, 졸이다, 비비다
불 조절: 센불, 강불, 중불, 중약불, 약불
기타: 밥, 쌀, 면, 라면, 국수, 스파게티, 파스타, 우동, 떡볶이떡, 김치, 깍두기, 멸치, 다시마, 육수, 비린맛, 잡내, 밑간, 양념장"""


async def transcribe_audio(audio_path: str) -> dict:
    """
    Whisper API를 사용하여 오디오를 텍스트로 변환합니다.
    word 단위 타임스탬프를 사용하여 문장 단위로 세그먼트를 구성합니다.

    Returns:
        dict: {
            'full_text': str,
            'segments': [
                {
                    'start': float,
                    'end': float,
                    'text': str
                }
            ]
        }
    """
    with open(audio_path, "rb") as audio_file:
        # word 단위 타임스탬프로 더 세밀하게 받기
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
            timestamp_granularities=["word", "segment"],
            language="ko",
            prompt=COOKING_PROMPT
        )

    # 원본 응답 로그 저장 (파일명 스템을 video_id로 사용)
    video_id = Path(audio_path).stem
    raw_response = response.model_dump() if hasattr(response, "model_dump") else getattr(response, "__dict__", {})
    save_log("whisper_raw", {"audio_path": audio_path, "response": raw_response}, video_id)

    # word 단위로 문장을 재구성
    segments = split_into_sentences(response)

    return {
        'full_text': response.text,
        'segments': segments,
        'language': getattr(response, 'language', 'ko'),
        'duration': getattr(response, 'duration', 0)
    }


def split_into_sentences(response) -> list:
    """
    Word 타임스탬프를 사용하여 문장 단위로 세그먼트를 분할합니다.
    문장 종결 패턴(~요, ~다, ~고, ~서 등)을 기준으로 분할합니다.
    """
    import re

    # word 정보가 있으면 사용, 없으면 segment 사용
    words = getattr(response, 'words', None)

    if not words:
        # word 정보 없으면 기존 segment 방식
        segments = []
        if hasattr(response, 'segments') and response.segments:
            for segment in response.segments:
                segments.append({
                    'start': getattr(segment, 'start', 0),
                    'end': getattr(segment, 'end', 0),
                    'text': getattr(segment, 'text', '').strip()
                })
        return segments

    # 문장 종결 패턴 (한국어)
    sentence_endings = re.compile(
        r'(요|다|죠|네요|세요|해요|하세요|합니다|됩니다|입니다|있어요|없어요|'
        r'주세요|드세요|넣으세요|볶으세요|썰어주세요|'
        r'거든요|잖아요|대요|래요|냐고요|는데요|어요|아요|'
        r'고요|구요|나요|까요|ㄹ까요|을까요|'
        r'니다|ㅂ니다|습니다)[\.\!\?]?$'
    )

    sentences = []
    current_words = []
    current_start = None

    for word in words:
        word_text = getattr(word, 'word', '').strip()
        word_start = getattr(word, 'start', 0)
        word_end = getattr(word, 'end', 0)

        if current_start is None:
            current_start = word_start

        current_words.append(word_text)

        # 문장 종결 패턴 체크
        is_sentence_end = sentence_endings.search(word_text)

        if is_sentence_end:
            # 띄어쓰기로 단어들 연결
            sentence_text = ' '.join(current_words).strip()
            if sentence_text:
                sentences.append({
                    'start': current_start,
                    'end': word_end,
                    'text': sentence_text
                })
            current_words = []
            current_start = None

    # 남은 단어들 처리
    if current_words:
        sentence_text = ' '.join(current_words).strip()
        if sentence_text:
            sentences.append({
                'start': current_start,
                'end': getattr(words[-1], 'end', 0),
                'text': sentence_text
            })

    # 문장이 없으면 원본 segment 반환
    if not sentences and hasattr(response, 'segments') and response.segments:
        for segment in response.segments:
            sentences.append({
                'start': getattr(segment, 'start', 0),
                'end': getattr(segment, 'end', 0),
                'text': getattr(segment, 'text', '').strip()
            })

    return sentences


def format_timestamp(seconds: float) -> str:
    """초를 MM:SS 형식으로 변환"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"
