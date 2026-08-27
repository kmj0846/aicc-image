---
name: aicc-image
description: ChatGPT 구독(codex CLI 내장 image_gen)으로 이미지를 생성·편집한다. API 키·장당 과금 없음. 사용자가 "이미지 그려줘", "이거 그림/사진으로 뽑아줘", "이 이미지에서 글자 지워줘/배경 바꿔줘"라고 하면 트리거.
---

# AICC 이미지 생성 (ChatGPT 구독 · codex image_gen)

동봉된 러너 `scripts/gpt-image.sh` 가 codex CLI 를 `codex exec` 로 실행해 내장
`image_gen` 도구로 이미지를 뽑는다. ChatGPT 구독 OAuth 로 돌므로 API 키·장당
과금이 없다. 장당 약 2분.

전제 조건은 codex CLI 설치와 ChatGPT 로그인(`codex login`) 1회뿐이고, 러너가 매번
자동 확인한다. 로그인이 풀려 있으면 사용자에게 `codex login` 실행을 요청한다
(Claude Code 터미널·앱에서는 입력창에 `! codex login` 을 치면 된다).

## 1. 재료 파악

- 용도·비율·장수를 확인한다. 말 안 했으면 기본값: 1장, 가로 16:9.
- 기존 이미지 편집(글자 제거, 배경 교체 등)이면 원본 경로를 받아 `-i` 로 첨부한다.

## 2. 프롬프트 작성 (영문)

- 키워드 나열 금지. **서술형 단락 하나**로 장면 전체를 쓴다.
- 매우 구체적으로: "서류 더미"가 아니라 "a towering stack of monthly settlement
  reports, edges perfectly squared" 수준.
- 긍정형 묘사만: "no people" 대신 "an empty office at dawn".
- 전문 사진 용어를 장면에 맞게: 렌즈(클로즈업 35~50mm, 공간 24~35mm 광각)와
  조명(방향·색온도)까지. 광원·그림자·재질이 맞물리게.
- 이미지 안에 글자를 넣지 않는 게 기본. 한글은 특히 깨진다 — 글자가 필요하면
  생성 후 폰트로 얹는 쪽을 제안한다.

## 3. 생성 (러너 실행)

```bash
~/.claude/skills/aicc-image/scripts/gpt-image.sh \
  --out "images/2026-08-27-slug/01-name.png" \
  --aspect "16:9" \
  "<영문 프롬프트>"
```

- 편집·참조: `-i <원본 절대경로>` 를 반복 첨부하고 `--timeout 420`. 편집이면
  프롬프트에 "EDIT the attached image: ..." 라고 지시.
- 저장 폴더는 요청 맥락에 맞게, 없으면 `images/{YYYY-MM-DD}-{슬러그}/`.
- 한 번에 한 장씩, 순차로 (병렬 금지 — codex 세션이 겹치면 느려진다).
- 마지막 줄이 `OK <경로>` 면 성공. `FAILED` 면 1회 재시도 후 에러를 그대로 보고한다.

## 4. 보고

이미지마다: ① 파일을 Read 로 열어 사용자가 바로 보게 ② 사용한 영문 프롬프트
③ 프롬프트 한글 번역 한 단락. 마지막에 "이 장만 다시, ___를 바꿔서"로 재생성할
수 있다고 안내한다.

## 주의

- 러너의 코덱스 옵션(`--ephemeral --ignore-user-config`, approval never)은 임의로
  빼지 말 것.
