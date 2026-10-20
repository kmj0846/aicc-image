"""링크 미리보기 이미지(site/og.png, 1200x630)를 만든다. build.py 전에 한 번 실행.

    python make_og.py path/to/pretendard/dist/public/static
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).parent
W, H = 1200, 630
IVORY, INK, SOFT, HONEY, BUTTER, BUTTER_DEEP = "#F7F2E9", "#3B3027", "#6F6256", "#876712", "#F3E4A4", "#E8D27A"


def rounded(img: Image.Image, size, radius) -> Image.Image:
    img = ImageOps.fit(ImageOps.exif_transpose(img).convert("RGB"), size, Image.LANCZOS)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *size), radius, fill=255)
    img.putalpha(mask)
    return img


def main(font_dir: str) -> None:
    font = lambda w, s: ImageFont.truetype(str(Path(font_dir) / f"Pretendard-{w}.otf"), s)
    im = Image.new("RGB", (W, H), IVORY)
    d = ImageDraw.Draw(im)

    d.text((72, 92), "호유홈", font=font("SemiBold", 28), fill=HONEY)
    d.text((72, 140), "우리집 톤 찾기", font=font("Bold", 76), fill=INK)
    d.text((72, 250), "집 사진으로 바닥·몰딩·벽 색을 읽어", font=font("Regular", 30), fill=SOFT)
    d.text((72, 294), "웜톤·쿨톤·뉴트럴 소품을 추천해요", font=font("Regular", 30), fill=SOFT)
    d.rounded_rectangle((72, 380, 412, 452), 36, fill=BUTTER, outline=BUTTER_DEEP, width=2)
    d.text((242, 416), "사진 올리고 확인하기", font=font("SemiBold", 26), fill=INK, anchor="mm")
    d.text((72, 520), "사진은 내 폰 안에서만 처리돼요", font=font("Regular", 22), fill=SOFT)

    # 오른쪽: 톤별 참고 사진 세 장
    x0, y0, cw, ch, gap = 560, 56, 184, 470, 12
    for i, (tone, label) in enumerate((("warm", "웜톤"), ("neutral", "뉴트럴"), ("cool", "쿨톤"))):
        src = sorted((HERE / "photos" / tone).glob("*.jpg"))[0]
        x = x0 + i * (cw + gap)
        im.paste(rounded(Image.open(src), (cw, ch), 28), (x, y0), rounded(Image.open(src), (cw, ch), 28))
        d.text((x + cw / 2, y0 + ch + 34), label, font=font("SemiBold", 24), fill=INK, anchor="mm")

    out = HERE / "site" / "og.png"
    out.parent.mkdir(exist_ok=True)
    im.save(out, optimize=True)
    print(out, out.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1])
