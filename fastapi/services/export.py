import os
import base64
from pathlib import Path
import markdown

# weasyprint가 없을 때도 서버가 뜨도록 선택적 로드
try:
    from weasyprint import HTML, CSS  # type: ignore
except Exception:  # ImportError 포함, 의존성 미설치 시
    HTML = None
    CSS = None


def generate_markdown(recipe_data: dict, frames: list, include_images: bool = True) -> str:
    """
    레시피 데이터를 Markdown 형식으로 변환합니다.
    """
    md_lines = []

    # 제목
    title = recipe_data.get('title', '레시피')
    md_lines.append(f"# {title}\n")

    # 설명
    if recipe_data.get('description'):
        md_lines.append(f"{recipe_data['description']}\n")

    # 기본 정보
    info_parts = []
    if recipe_data.get('servings'):
        info_parts.append(f"**인분**: {recipe_data['servings']}")
    if recipe_data.get('total_time'):
        info_parts.append(f"**조리시간**: {recipe_data['total_time']}")
    if info_parts:
        md_lines.append(" | ".join(info_parts) + "\n")

    md_lines.append("---\n")

    # 재료
    md_lines.append("## 재료\n")
    ingredients = recipe_data.get('ingredients', [])
    if ingredients:
        for ing in ingredients:
            name = ing.get('name', '')
            amount = ing.get('amount', '')
            unit = ing.get('unit', '')
            note = ing.get('note', '')

            ingredient_str = f"- {name}"
            if amount or unit:
                ingredient_str += f" {amount}{unit}"
            if note:
                ingredient_str += f" ({note})"
            md_lines.append(ingredient_str)
        md_lines.append("")
    else:
        md_lines.append("- 재료 정보가 없습니다.\n")

    md_lines.append("---\n")

    # 조리 순서
    md_lines.append("## 조리 순서\n")
    steps = recipe_data.get('steps', [])

    # 프레임 정보를 step_number로 매핑
    frame_map = {f['step_number']: f for f in frames}

    for step in steps:
        step_num = step.get('step_number', 0)
        instruction = step.get('instruction', '')
        tips = step.get('tips', '')
        timestamp = step.get('timestamp', 0)

        # 타임스탬프 포맷
        time_str = format_time(timestamp)

        md_lines.append(f"### {step_num}. {instruction}")
        md_lines.append(f"*({time_str})*\n")

        # 이미지 포함
        if include_images and step_num in frame_map:
            frame_info = frame_map[step_num]
            frame_filename = frame_info.get('frame_filename', '')
            md_lines.append(f"![Step {step_num}](frames/{frame_filename})\n")

        # 팁
        if tips:
            md_lines.append(f"> 💡 **Tip**: {tips}\n")

        md_lines.append("")

    # 전체 팁
    overall_tips = recipe_data.get('tips', [])
    if overall_tips:
        md_lines.append("---\n")
        md_lines.append("## 요리 팁\n")
        for tip in overall_tips:
            md_lines.append(f"- {tip}")
        md_lines.append("")

    return "\n".join(md_lines)


def generate_pdf(recipe_data: dict, frames: list, output_path: str, frames_dir: str) -> bool:
    """
    레시피 데이터를 PDF로 변환합니다.
    """
    if HTML is None or CSS is None:
        # weasyprint 미설치 시 PDF 생성을 건너뜀
        return False

    # HTML 템플릿 생성
    html_content = generate_html(recipe_data, frames, frames_dir)

    css = CSS(string='''
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: #333;
        }
        h1 {
            color: #e67e22;
            border-bottom: 3px solid #e67e22;
            padding-bottom: 10px;
        }
        h2 {
            color: #2c3e50;
            margin-top: 30px;
        }
        h3 {
            color: #34495e;
        }
        .info {
            background: #f8f9fa;
            padding: 10px 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        .ingredients {
            background: #fff3e0;
            padding: 15px 20px;
            border-radius: 8px;
            border-left: 4px solid #e67e22;
        }
        .ingredients ul {
            margin: 0;
            padding-left: 20px;
        }
        .step {
            margin: 20px 0;
            padding: 15px;
            background: #fafafa;
            border-radius: 8px;
        }
        .step-header {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .step-number {
            background: #e67e22;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        .timestamp {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .step-image {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 10px 0;
        }
        .tip {
            background: #e8f6f3;
            padding: 10px 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #1abc9c;
        }
        .overall-tips {
            background: #fef9e7;
            padding: 15px 20px;
            border-radius: 8px;
            margin-top: 30px;
        }
    ''')

    try:
        html = HTML(string=html_content)
        html.write_pdf(output_path, stylesheets=[css])
        return True
    except Exception as e:
        print(f"PDF generation error: {e}")
        return False


def generate_html(recipe_data: dict, frames: list, frames_dir: str) -> str:
    """HTML 형식으로 변환 (PDF 생성용)"""
    frame_map = {f['step_number']: f for f in frames}

    title = recipe_data.get('title', '레시피')
    description = recipe_data.get('description', '')

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
    </head>
    <body>
        <h1>{title}</h1>
        <p>{description}</p>
    """

    # 기본 정보
    info_parts = []
    if recipe_data.get('servings'):
        info_parts.append(f"<strong>인분:</strong> {recipe_data['servings']}")
    if recipe_data.get('total_time'):
        info_parts.append(f"<strong>조리시간:</strong> {recipe_data['total_time']}")
    if info_parts:
        html += f'<div class="info">{" | ".join(info_parts)}</div>'

    # 재료
    html += '<h2>재료</h2><div class="ingredients"><ul>'
    for ing in recipe_data.get('ingredients', []):
        name = ing.get('name', '')
        amount = ing.get('amount', '')
        unit = ing.get('unit', '')
        note = ing.get('note', '')
        ing_str = f"{name} {amount}{unit}"
        if note:
            ing_str += f" ({note})"
        html += f"<li>{ing_str}</li>"
    html += '</ul></div>'

    # 조리 순서
    html += '<h2>조리 순서</h2>'
    for step in recipe_data.get('steps', []):
        step_num = step.get('step_number', 0)
        instruction = step.get('instruction', '')
        tips = step.get('tips', '')
        timestamp = step.get('timestamp', 0)
        time_str = format_time(timestamp)

        html += f'''
        <div class="step">
            <div class="step-header">
                <div class="step-number">{step_num}</div>
                <div>
                    <strong>{instruction}</strong>
                    <span class="timestamp">({time_str})</span>
                </div>
            </div>
        '''

        # 이미지 삽입 (base64)
        if step_num in frame_map:
            frame_path = frame_map[step_num].get('frame_path', '')
            if os.path.exists(frame_path):
                with open(frame_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
                html += f'<img class="step-image" src="data:image/jpeg;base64,{img_data}" />'

        if tips:
            html += f'<div class="tip">💡 <strong>Tip:</strong> {tips}</div>'

        html += '</div>'

    # 전체 팁
    overall_tips = recipe_data.get('tips', [])
    if overall_tips:
        html += '<div class="overall-tips"><h3>요리 팁</h3><ul>'
        for tip in overall_tips:
            html += f"<li>{tip}</li>"
        html += '</ul></div>'

    html += '</body></html>'
    return html


def format_time(seconds: float) -> str:
    """초를 MM:SS 형식으로 변환"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"
