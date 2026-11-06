# 포트폴리오 방명록 API

AIM 커리어 트윈의 체험 C를 위한 FastAPI + SQLite 참고 구현입니다.
**이 버전의 코드는 Codex가 구현했습니다. 본인의 직접 코딩 체험 완료나 몰입도 증빙으로 쓰지 않습니다.**

## 실행

Python 3.9 이상에서:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

- 상태 확인: http://127.0.0.1:8000/ → `{"status":"ok"}`
- API 실행 화면: http://127.0.0.1:8000/docs
- `POST /guestbook`: `{"name":"방문자","content":"안녕하세요"}`
- `GET /guestbook`: 최신순 목록

데이터는 `id`, `name`(1~50자), `content`(1~500자), `created_at`(서버의 UTC 시각)으로 구성합니다.
앞뒤 공백을 제거하며 공백뿐인 입력은 422로 거절합니다. SQL 값은 `?` 파라미터로 전달합니다.
DB는 기본적으로 프로젝트 폴더의 `guestbook.db`이며 `GUESTBOOK_DB` 환경변수로 경로를 바꿀 수 있습니다.
DB와 가상환경은 Git에 포함하지 않습니다.

## 검증

```bash
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

## 작업 구분

- 코드·정적 포트폴리오: AI 작성 준비본
- 개인 소개 내용·최종 진로·체험 소감·확신도: 본인 확인 대기
- 로컬 테스트 요청: 기능 확인용 합성 데이터이며 실제 방문자 반응이 아님
- 공개 서버 배포 전: 영구 저장소, 게시물 관리, 요청 제한 등을 운영 환경에 맞게 준비해야 함

공식 참고: https://fastapi.tiangolo.com/tutorial/first-steps/ , https://fastapi.tiangolo.com/advanced/events/
