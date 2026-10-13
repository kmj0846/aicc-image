#!/usr/bin/env python3
"""예시 데이터(거실 사진 + 미리 만든 분석 결과)를 index.html에 넣어 배포용 HTML을 만든다.

사진은 저장소에 커밋하지 않는다. 사용법:
  python3 build_sample.py OUT.html PHOTO1 PHOTO2 ... [--analysis sample_analysis.json]
분석 JSON의 좌표는 사진을 가로 2000(세로 사진은 1500) 기준으로 본 픽셀값이며, 여기서 0~1 비율로 바꾼다.
"""
import base64, io, json, sys, pathlib
from PIL import Image, ImageDraw, ImageOps

HERE = pathlib.Path(__file__).parent


def photo_data_url(path, max_side=1400):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    im.thumbnail((max_side, max_side), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=82, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), im.size


def sample_clock():
    """흰 배경 위 원목 테 벽시계 (배경 지우기 기능을 보여주려고 일부러 흰 배경)."""
    S = 600; im = Image.new("RGB", (S, S), (248, 248, 246)); d = ImageDraw.Draw(im)
    c = S // 2; R = 250
    d.ellipse([c - R, c - R, c + R, c + R], fill=(158, 106, 60))
    d.ellipse([c - R + 10, c - R + 10, c + R - 10, c + R - 10], fill=(176, 122, 72))
    r2 = R - 34; d.ellipse([c - r2, c - r2, c + r2, c + r2], fill=(244, 240, 232))
    import math
    for i in range(12):
        a = math.pi * 2 * i / 12; L = 26 if i % 3 == 0 else 14; w = 7 if i % 3 == 0 else 4
        x1, y1 = c + math.sin(a) * (r2 - 18), c - math.cos(a) * (r2 - 18)
        x2, y2 = c + math.sin(a) * (r2 - 18 - L), c - math.cos(a) * (r2 - 18 - L)
        d.line([x1, y1, x2, y2], fill=(40, 38, 34), width=w)
    def hand(deg, ln, w):
        a = math.radians(deg); d.line([c, c, c + math.sin(a) * ln, c - math.cos(a) * ln], fill=(40, 38, 34), width=w)
    hand(305, 120, 12); hand(62, 170, 7)
    d.ellipse([c - 12, c - 12, c + 12, c + 12], fill=(40, 38, 34))
    buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def norm(analysis, sizes):
    """픽셀 기준 좌표(가로 사진 2000×1500, 세로 사진 1500×2000)를 비율로 변환."""
    def dims(i):
        w, h = sizes[i]
        return (2000, 1500) if w >= h else (1500, 2000)
    for key in ("remove", "add"):
        for item in analysis.get(key, []):
            for m in item.get("marks", []):
                W, H = dims(m["photo"])
                if "box" in m:
                    x, y, w, h = m["box"]; m["box"] = [round(x / W, 4), round(y / H, 4), round(w / W, 4), round(h / H, 4)]
                if "quad" in m:
                    m["quad"] = [[round(x / W, 4), round(y / H, 4)] for x, y in m["quad"]]
    for g in analysis.get("lighting", {}).get("glows", []):
        W, H = dims(g["photo"]); g["x"] = round(g["x"] / W, 4); g["y"] = round(g["y"] / H, 4)
    return analysis


def main():
    args = sys.argv[1:]
    ana_path = HERE / "sample_analysis.json"
    if "--analysis" in args:
        i = args.index("--analysis"); ana_path = pathlib.Path(args[i + 1]); del args[i:i + 2]
    out, photos = args[0], args[1:]
    urls, sizes = zip(*(photo_data_url(p) for p in photos))
    spec = json.loads(ana_path.read_text())
    analysis = norm(spec["analysis"], sizes)
    t = spec["tryon"]; W, H = (2000, 1500) if sizes[t["photo"]][0] >= sizes[t["photo"]][1] else (1500, 2000)
    tryon = {"photo": t["photo"], "cx": t["cx"] / W, "cy": t["cy"] / H, "width": t["width"], "name": t["name"],
             "product": sample_clock(), "eval": t["eval"]}
    data = {"photos": list(urls), "analysis": analysis, "options": spec["options"], "tryon": tryon}
    html = (HERE / "index.html").read_text()
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = html.replace("/*__SAMPLE__*/null", blob, 1)
    pathlib.Path(out).write_text(html)
    print(out, f"{len(html) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
