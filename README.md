# 포트폴리오 방명록 API

김희민의 포트폴리오 페이지와 FastAPI + SQLite 방명록입니다.
**코드와 초안은 AI(Codex, Claude)가 구현했습니다. 본인의 독립 구현 증빙으로 쓰지 않습니다. 본인 수정은 커밋 기록으로 구분합니다.**

## 실행

Python 3.9 이상에서:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

- 포트폴리오: http://127.0.0.1:8000/
- 상태 확인: http://127.0.0.1:8000/health → `{"status":"ok"}`
- API 실행 화면: http://127.0.0.1:8000/docs
- `POST /guestbook`: `{"name":"방문자","content":"안녕하세요"}`
- `GET /guestbook`: 최신순 목록

데이터는 `id`, `name`(1~10자), `content`(1~500자), `created_at`(서버의 UTC 시각)으로 구성합니다.
앞뒤 공백을 제거하며 공백뿐인 입력은 422로 거절합니다. SQL 값은 `?` 파라미터로 전달합니다.
DB는 기본적으로 프로젝트 폴더의 `guestbook.db`이며 `GUESTBOOK_DB` 환경변수로 경로를 바꿀 수 있습니다.
DB와 가상환경은 Git에 포함하지 않습니다.

## 배포

`render.yaml`에 Render 무료 웹 서비스 설정이 있습니다. 무료 요금에서는 15분간 접속이 없으면 서버가 잠들고, SQLite 파일은 재시작·재배포·잠들 때 초기화되어 방명록 글이 사라집니다.
글을 계속 보관하려면 영구 저장소가 있는 환경에서 `GUESTBOOK_DB`를 그 경로로 설정합니다. Dockerfile은 컨테이너 빌드를 검증하지 않았습니다.

## 검증

```bash
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

## 작업 구분

- 등록·목록 API는 `guestbook.py`로 분리해 AI 지원으로 재작성했습니다. 기존 API 구현 본문을 읽지 않고 요청·응답 조건과 DB 구조를 기준으로 작성했으며, 본인이 독립 구현한 체험으로 기록하지 않습니다.
- `main.py`는 기존 두 API 구현 대신 새 라우터를 연결합니다. DB 초기화와 다른 페이지 기능은 기존 구성을 유지합니다.

- 포트폴리오 문구·화면, 첫 화면 연결, 코드 정리, 배포 설정: Claude 초안 (본인 검토 전)
- 로컬 테스트 요청: 기능 확인용 합성 데이터이며 실제 방문자 반응이 아님
- 공개 서버 배포 전: 영구 저장소, 게시물 관리, 요청 제한 등을 운영 환경에 맞게 준비해야 함

공식 참고: https://fastapi.tiangolo.com/tutorial/first-steps/ , https://fastapi.tiangolo.com/advanced/events/
