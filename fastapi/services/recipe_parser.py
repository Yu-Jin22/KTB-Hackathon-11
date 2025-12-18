import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RECIPE_PARSE_PROMPT = """당신은 자취생을 위한 요리 레시피 전문가입니다.
YouTube 쇼츠 요리 영상의 음성 텍스트를 분석하여, 초보자도 쉽게 따라할 수 있도록 **매우 상세한** 레시피로 정리해주세요.

## 중요: 상세한 설명 원칙
- 각 조리 단계는 **구체적인 행동**을 포함해야 합니다
- "썰어주세요" → "0.5cm 두께로 얇게 썰어주세요" 처럼 구체적으로
- 불 조절, 시간, 색깔 변화 등 **감각적 지표**를 포함하세요
- 자취생이 처음 요리해도 따라할 수 있게 친절하게 작성하세요

- steps의 timestamp는 아래 segments의 시간 범위(start, end)를 근거로 정한다.
- 각 step은 반드시 source_segment_ids를 포함하고,
- timestamp는 start = min(선택된 segment.start)로 계산한다.
- 모델은 start/end 숫자를 새로 만들지 말고 segments에서만 가져온다(0.1초 반올림만 허용).



## 출력 형식 (반드시 JSON으로)
{
    "title": "요리 이름",
    "description": "요리에 대한 설명과 특징 (맛, 난이도, 추천 상황 등 2-3문장)",
    "servings": "인분 수",
    "total_time": "총 조리 시간",
    "difficulty": "난이도 (쉬움/보통/어려움)",
    "ingredients": [
        {
            "name": "재료명",
            "amount": "양",
            "unit": "단위",
            "note": "손질법이나 대체재료 (예: 없으면 OO로 대체 가능)"
        }
    ],
    "steps": [
        {
            "step_number": 1,
            "instruction": "상세한 조리 단계 설명 (구체적인 방법, 시간, 불 세기 등 포함)",
            "timestamp": 0.0, 
            "duration": "이 단계 소요 시간",
            "details": "추가 설명 (왜 이렇게 하는지, 어떤 상태가 되어야 하는지)",
            "tips": "초보자를 위한 팁이나 주의사항"
        }
    ],
    "tips": ["전체적인 요리 팁들 - 보관법, 응용법 등"]
}

## 상세 작성 예시

나쁜 예:
- "양파를 볶아주세요"

좋은 예:
- "중불에서 양파가 투명해질 때까지 약 2-3분간 볶아주세요. 양파가 갈색으로 변하기 시작하면 불을 줄이세요."

## 주의사항
1. 재료의 양과 단위를 명확히 분리 (예: "2스푼" → amount: "2", unit: "스푼")
2. 각 조리 단계에 해당하는 타임스탬프를 정확히 매핑
3. **조리 단계는 가능한 세분화**하여 작성 (영상에서 빠르게 넘어가도 상세히)
4. 불 세기(약불/중불/강불), 시간, 완료 상태를 반드시 포함
5. 영상에서 직접 언급하지 않았더라도, 요리 상식으로 필요한 정보는 추가
6. 한국어로 친근하게 작성
7. 반드시 유효한 JSON 형식으로 출력
"""


async def parse_recipe(transcript_data: dict) -> dict:
    """
    GPT-4o를 사용하여 음성 텍스트를 구조화된 레시피로 변환합니다.

    Args:
        transcript_data: {
            'full_text': str,
            'segments': [{'start': float, 'end': float, 'text': str}]
        }

    Returns:
        dict: 구조화된 레시피 데이터
    """
    # 세그먼트 정보를 포함한 텍스트 구성
    segments_text = ""
    for seg in transcript_data.get('segments', []):
        start = seg['start']
        end = seg['end']
        text = seg['text']
        segments_text += f"[{start:.1f}s - {end:.1f}s]: {text}\n"

    user_message = f"""다음은 요리 영상의 음성 텍스트입니다:

## 전체 텍스트
{transcript_data.get('full_text', '')}

## 타임스탬프별 세그먼트
{segments_text}

이 내용을 분석하여 구조화된 레시피 JSON을 생성해주세요."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": RECIPE_PARSE_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    result_text = response.choices[0].message.content

    try:
        recipe_data = json.loads(result_text)
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 기본 구조 반환
        recipe_data = {
            "title": "레시피",
            "description": "파싱 중 오류가 발생했습니다.",
            "ingredients": [],
            "steps": [],
            "raw_text": transcript_data.get('full_text', '')
        }

    return recipe_data


def get_step_timestamps(recipe_data: dict) -> list:
    """레시피 단계별 타임스탬프 목록 추출/정규화"""
    timestamps = []
    for step in recipe_data.get('steps', []):
        raw_ts = step.get('timestamp')
        parsed_ts = parse_timestamp_value(raw_ts)
        if parsed_ts is None:
            continue
        timestamps.append({
            'step_number': step.get('step_number', 0),
            'timestamp': parsed_ts,
            'instruction': step.get('instruction', '')
        })
    # 타임스탬프 기준 정렬로 ffmpeg 캡처 순서 고정
    return sorted(timestamps, key=lambda item: item['timestamp'])


def parse_timestamp_value(value) -> float | None:
    """
    다양한 형태의 timestamp 값을 초 단위 float로 정규화한다.
    허용: float/int, "12.3", "01:23", "00:01:23"
    """
    if value is None:
        return None

    # 이미 숫자인 경우
    if isinstance(value, (int, float)):
        return float(value) if value >= 0 else None

    if isinstance(value, str):
        text = value.strip().lower()
        # 숫자 문자열 "12.3" 또는 "12"
        try:
            num = float(text.replace('s', ''))
            if num >= 0:
                return num
        except ValueError:
            pass

        # MM:SS 또는 HH:MM:SS
        parts = text.split(':')
        if 2 <= len(parts) <= 3 and all(p.replace('.', '', 1).isdigit() for p in parts):
            try:
                parts = [float(p) for p in parts]
                if len(parts) == 2:
                    minutes, seconds = parts
                    total = minutes * 60 + seconds
                else:
                    hours, minutes, seconds = parts
                    total = hours * 3600 + minutes * 60 + seconds
                return total if total >= 0 else None
            except Exception:
                return None

    return None
