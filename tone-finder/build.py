"""src.html → index.html·site/index.html (웹에 올리는 완성 파일) + artifact.html (Claude 아티팩트용).

페이지에 쓰인 글자만 남긴 Pretendard 서브셋을 woff2로 만들어 파일 안에 직접 넣습니다.
src.html의 문구를 바꾸면 이 스크립트를 다시 실행하세요.

    pip install fonttools brotli pillow
    python build.py path/to/pretendard/dist/web/static/woff2
"""
import base64
import io
import json
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from PIL import Image, ImageOps

HERE = Path(__file__).parent
WEIGHTS = {400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold"}
SITE_URL = "https://fastidious-lily-328df5.netlify.app"  # Netlify 주소를 바꾸면 여기도 바꾸고 다시 빌드
DESCRIPTION = "집 사진 한 장으로 바닥·몰딩·벽 색을 읽어 웜톤·쿨톤·뉴트럴 소품을 추천해요. 사진은 내 폰 안에서만 처리돼요."
ICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
    "%3Crect width='64' height='64' rx='14' fill='%23F3E4A4'/%3E"
    "%3Cpath d='M14 32 32 16l18 16v16a2 2 0 0 1-2 2H16a2 2 0 0 1-2-2z' fill='%23C49A6C'/%3E"
    "%3Crect x='27' y='36' width='10' height='14' fill='%23F7F2E9'/%3E%3C/svg%3E"
)
META = (
    f'<meta name="description" content="{DESCRIPTION}">\n'
    '<meta property="og:type" content="website">\n'
    '<meta property="og:title" content="우리집 톤 찾기 · 호유홈">\n'
    f'<meta property="og:description" content="{DESCRIPTION}">\n'
    f'<meta property="og:url" content="{SITE_URL}/">\n'
    f'<meta property="og:image" content="{SITE_URL}/og.png">\n'
    '<meta property="og:image:width" content="1200">\n'
    '<meta property="og:image:height" content="630">\n'
    '<meta name="twitter:card" content="summary_large_image">\n'
    '<meta name="theme-color" content="#F7F2E9">\n'
    f'<link rel="icon" href="{ICON}">\n'
)


def subset_font(path: Path, text: str) -> str:
    font = TTFont(path)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def load_photos() -> dict:
    """photos/<톤>/ 폴더의 사진을 긴 변 1000px JPEG로 줄여 data URI 목록으로 만든다."""
    photos = {}
    for tone in ("warm", "cool", "neutral"):
        uris = []
        for f in sorted((HERE / "photos" / tone).glob("*")):
            if f.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
                continue
            img = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
            img.thumbnail((1000, 1000))
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=74, optimize=True, progressive=True)
            uris.append("data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode())
        photos[tone] = uris
    return photos


def main(font_dir: str) -> None:
    src = (HERE / "src.html").read_text(encoding="utf-8")
    text = src + "".join(chr(c) for c in range(0x20, 0x7F)) + "…·×①②③"
    faces = []
    for weight, name in WEIGHTS.items():
        data = subset_font(Path(font_dir) / f"Pretendard-{name}.woff2", text)
        faces.append(
            f'@font-face{{font-family:"Pretendard";font-weight:{weight};font-style:normal;'
            f'font-display:swap;src:url(data:font/woff2;base64,{data}) format("woff2");}}'
        )
    page = src.replace("/*@FONTS@*/", "\n".join(faces))
    photos = load_photos()
    print({k: len(v) for k, v in photos.items()})
    page = page.replace("/*@PHOTOS@*/{ warm: [], cool: [], neutral: [] }", json.dumps(photos))

    (HERE / "artifact.html").write_text(page, encoding="utf-8")
    # 단독 실행용: 제목·미리보기 정보를 <head>에 둬야 인스타·카톡 링크 미리보기에 잡힌다.
    head_end = page.index("<style>")
    head, body = page[:head_end], page[head_end:]
    standalone = (
        '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + head + META + "</head>\n<body>\n" + body + "\n</body>\n</html>\n"
    )
    for out in (HERE / "index.html", HERE / "site" / "index.html"):
        out.parent.mkdir(exist_ok=True)
        out.write_text(standalone, encoding="utf-8")
    print(f"index.html {len(standalone) // 1024}KB")


if __name__ == "__main__":
    main(sys.argv[1])
