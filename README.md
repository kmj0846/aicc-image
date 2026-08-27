# aicc-image

Claude Code에서 ChatGPT 구독으로 이미지를 생성하는 스킬입니다.

Claude는 이미지를 직접 그리지 못합니다. 이 스킬은 같은 컴퓨터에 설치된 codex CLI를 Claude가 대신 실행해서, codex에 내장된 image_gen 도구로 이미지를 만들게 합니다. 인증은 ChatGPT 로그인 1회로 끝나고, API 키와 장당 과금이 없습니다. ChatGPT 구독 사용량 안에서 해결됩니다.

## 요구사항

- Claude Code (터미널, 데스크톱 앱, IDE 확장 어디든. 단 claude.ai 웹의 클라우드 세션은 제외)
- [codex CLI](https://developers.openai.com/codex/cli) 설치
- ChatGPT 유료 구독

## 설치 (1회)

```bash
git clone https://github.com/henryoon0/aicc-image ~/.claude/skills/aicc-image
codex login   # ChatGPT 계정으로 로그인
```

이게 전부입니다. 이후에는 아무것도 관리할 필요가 없습니다.

## 사용법

Claude Code에서 이렇게 말하면 됩니다.

- "새벽 창가의 커피잔 사진 그려줘"
- "이 이미지에서 글자 지워줘"
- `/aicc-image` 로 직접 부를 수도 있습니다.

Claude가 영문 프롬프트를 작성하고, 동봉된 `scripts/gpt-image.sh`로 생성부터 결과 검증까지 처리합니다. 장당 약 2분 걸립니다.

## 동작 원리

1. Claude가 요청을 서술형 영문 프롬프트로 다듬는다.
2. 러너 스크립트가 `codex exec`를 1회성 모드로 실행한다. 세션 기록을 남기지 않고, API 키 환경변수를 제거해 구독 경로만 남긴다.
3. codex의 내장 image_gen이 이미지를 만들면, 스크립트가 파일 존재와 크기를 검증한다.

## 라이선스

MIT
