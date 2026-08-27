#!/bin/bash
# aicc-image runner — ChatGPT 구독(codex exec 내장 image_gen)으로 이미지 생성.
# API 키 불필요. 인증은 `codex login`(ChatGPT sign-in) 1회로 끝.
#
# usage:
#   gpt-image.sh --out <파일.png> [--aspect "16:9"] [--timeout 300] [-i 참조이미지]... "영문 프롬프트"
#
# 프롬프트는 마지막 인자 하나로 준다. 참조 이미지는 -i 를 반복해 여러 장 첨부 가능
# (편집 대상 원본도 -i 로 넣고 프롬프트에서 "EDIT the attached image"라고 지시).
set -euo pipefail

OUT=""
ASPECT="16:9"
TIMEOUT_SEC=300
REFS=()

while [[ $# -gt 1 ]]; do
  case "$1" in
    --out)     OUT="$2"; shift 2 ;;
    --aspect)  ASPECT="$2"; shift 2 ;;
    --timeout) TIMEOUT_SEC="$2"; shift 2 ;;
    -i)        REFS+=("$2"); shift 2 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done
PROMPT="${1:-}"

[[ -n "$OUT" && -n "$PROMPT" ]] || { echo "usage: gpt-image.sh --out FILE [--aspect R] [-i REF]... PROMPT" >&2; exit 2; }

# 1) 인증: ChatGPT 로그인만 허용 (API 키 과금 경로 차단)
LOGIN=$(codex login status 2>&1 || true)
if [[ "$LOGIN" != *"ChatGPT"* ]]; then
  echo "codex 가 ChatGPT 로 로그인돼 있지 않습니다. 터미널에서 'codex login' 을 실행해 주세요." >&2
  echo "(현재 상태: $LOGIN)" >&2
  exit 3
fi

OUT_DIR=$(cd "$(dirname "$OUT")" 2>/dev/null && pwd) || { mkdir -p "$(dirname "$OUT")"; OUT_DIR=$(cd "$(dirname "$OUT")" && pwd); }
OUT_NAME=$(basename "$OUT")

ARGS=(exec --skip-git-repo-check --ephemeral --ignore-user-config --color never
  -s workspace-write -c 'approval_policy="never"' -C "$OUT_DIR")
for r in "${REFS[@]:-}"; do [[ -n "$r" ]] && ARGS+=(-i "$r"); done
ARGS+=(-)

# 2) 생성: 프롬프트는 stdin 으로. OPENAI_API_KEY 를 지워 구독 경로만 남긴다.
env -u OPENAI_API_KEY timeout "$TIMEOUT_SEC" codex "${ARGS[@]}" <<EOF
Use your built-in image_gen tool to produce exactly one image, then save it as a PNG file
named ${OUT_NAME} in the current working directory. Aspect ratio: ${ASPECT}.
Do not call any external API. After saving, print the absolute file path.
BEGIN USER PROMPT
${PROMPT}
END USER PROMPT
EOF

# 3) 검증: 파일이 실제로 생겼는지 (50KB 미만이면 실패로 간주)
FULL="$OUT_DIR/$OUT_NAME"
SIZE=$(stat -f%z "$FULL" 2>/dev/null || echo 0)
if [[ "$SIZE" -lt 51200 ]]; then
  echo "FAILED: $FULL 이 만들어지지 않았거나 비정상적으로 작습니다 (${SIZE} bytes)" >&2
  exit 4
fi
echo "OK $FULL (${SIZE} bytes)"
