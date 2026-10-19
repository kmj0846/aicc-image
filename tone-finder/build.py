"""src.html → index.html (단독 실행용 완성 파일) + artifact.html (Claude 아티팩트용).

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
    standalone = (
        '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        "</head>\n<body>\n" + page + "\n</body>\n</html>\n"
    )
    (HERE / "index.html").write_text(standalone, encoding="utf-8")
    print(f"index.html {len(standalone) // 1024}KB")


if __name__ == "__main__":
    main(sys.argv[1])
