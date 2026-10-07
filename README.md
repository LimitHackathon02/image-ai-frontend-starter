# HyperCLOVA X 해커톤 백엔드

주제가 달라져도 `tasks.json`의 프롬프트와 결과 필드를 바꿔 사용할 수 있는 Python + FastAPI 백엔드입니다. 실행 시 다른 AI 서비스를 호출하지 않으며 HyperCLOVA X REST API만 사용합니다. 기본값은 외부 호출 없는 **모의 실행**입니다.

사용자 설명상 대회는 사전 준비가 기본적으로 금지되어 있습니다. **이 프로젝트는 사전 학습·연결 연습용입니다. 코드·설정·가이드의 반입 및 제출물 재사용이 허용된다고 가정하지 않습니다.** 현장에서 직접 작성할 최소 흐름은 `FIELD_GUIDE.md`에 정리했습니다.

## 이미지 → 텍스트 기능

기존 `POST /api/vision`에 `task=image_text`를 추가했습니다. 기본 `image_analyze`와 기존 task의 요청·응답은 유지합니다. 프론트 화면 및 요약·일정·장소·지도 기능은 추가하지 않았습니다.

### Windows PowerShell 실행 (Python 3.11 이상)

프로젝트 폴더에서 실행하세요. Python이 다른 경로에 있다면 해당 실행 파일로 venv를 생성해도 됩니다.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

활성화가 실행 정책에 막히면 활성화 없이 `.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt` 및 `.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`를 실행하세요. 기본 `MOCK_MODE=true`는 키 없이 실행됩니다.

### /docs 업로드 및 팀 API 계약

http://localhost:8000/docs → POST /api/vision → Try it out → file 한 장 선택 → task를 `image_text`로 변경 → Execute. question은 기존 호환성을 위해 유지하지만 image_text에서는 고정 전사 지시를 사용하므로 무시합니다. use_cache=false로 캐시를 끌 수 있습니다. TEAM_API_KEY를 설정했다면 요청에 X-Team-Key 헤더가 필요합니다(기본값은 빈 값).

요청은 multipart/form-data이며 file, question, task, use_cache 필드를 유지합니다. 기존 examples/frontend.js는 수정하지 않았습니다.

```powershell
curl.exe -X POST http://localhost:8000/api/vision -F "file=@C:/images/sample.png" -F "task=image_text" -F "use_cache=false"
```

기본 모의 응답 예시:

```json
{"task":"image_text","output":{"text":"[MOCK] 첫 번째 줄\n두 번째 줄"},"model":"HCX-005","mock":true,"cached":false,"finish_reason":"stop","usage":{"prompt_tokens":0,"completion_tokens":0,"total_tokens":0}}
```

실제 응답은 mock=false이며 output.text에 읽힌 원문을 반환합니다. 원문 언어와 줄바꿈을 보존하도록 지시하고, 글자가 없으면 `output: {"text": ""}`로 정상 반환합니다. JSON의 `\n`은 파싱하면 줄바꿈이 됩니다. 다른 담당자는 `result["output"]["text"]`를 자신의 텍스트 처리 기능에 전달하세요. mock=true는 고정 연결 예시이며 실제 인식 결과가 아닙니다. 이미지 설명이 필요하면 기존 image_analyze의 description, visible_text, suggestions, uncertainties를 사용하세요.

### 이미지 제한과 오류

실제 디코딩 형식으로 PNG/JPEG/WEBP/BMP를 검사합니다. 확장자와 Content-Type이 잘못되어도 실제 지원 이미지이면 허용합니다. 기본 원본 제한은 10MiB(10,485,760바이트), 20,000,000픽셀, 가로·세로 최소 4px입니다. 용량 한도+1바이트까지만 읽고, 픽셀 제한은 전체 디코딩 전에 검사합니다. verify 후 다시 열어 전체 픽셀을 디코딩하여 손상을 검사합니다. 업로드 스풀 파일은 성공·실패 모두 닫으며 별도 이미지 파일은 저장하지 않습니다. Starlette multipart 수신은 임시 스풀을 사용할 수 있으므로 운영 환경에서는 프록시 요청 본문 제한도 설정하세요.

기존처럼 긴 변 1,280px 이하 JPEG로 변환하고 5:1을 넘는 비율에는 흰 여백을 추가합니다. EXIF 방향을 반영하고 원본 메타데이터는 보내지 않습니다. 애니메이션 WEBP는 첫 프레임을 처리합니다. 축소된 작은 글자, 복잡한 문서의 읽기 순서와 전사 정확도는 실제 호출에서 확인해야 합니다.

| 상황 | HTTP 상태 |
|---|---|
| 빈 파일, 비이미지, 손상, 미지원 형식, 최소 크기 미달 | 422 |
| 용량 또는 픽셀 초과 | 413 |
| 실제 모드 키 미설정 | 503 |
| 제공자 타임아웃 | 504 |
| 제공자 인증·호출 제한·연결 실패·잘못된 응답·JSON 오류·출력 잘림 | 502 (기존 계약 유지) |
| 로컬 호출 횟수·누적 토큰 한도 | 429 |

오류는 `{"detail":"안전한 오류 설명"}`입니다. 공급자 본문이나 키를 반환하지 않으며 실제 실패를 모의 성공으로 숨기거나 자동 재시도하지 않습니다.

### 환경 설정 및 주제 확정 후 변경 위치

| 변수 | 기본값 / 용도 |
|---|---|
| MOCK_MODE | true: 고정 모의 응답 / false: 실제 호출 |
| CLOVA_API_KEY | 빈 값; 실제 실행에 필요한 키 |
| CLOVA_BASE_URL | https://clovastudio.stream.ntruss.com |
| CLOVA_VISION_MODEL | HCX-005; 지급받은 이미지 지원 모델 확인 |
| CLOVA_TIMEOUT_SECONDS | 60 |
| IMAGE_MAX_BYTES | 10485760; 원본 바이트 한도 |
| IMAGE_MAX_PIXELS | 20000000; 원본 가로×세로 한도 |
| DATABASE_PATH / TASKS_PATH | data/hackathon.sqlite3 / tasks.json |
| CACHE_TTL_SECONDS | 3600; 0이면 캐시 비활성화 |
| MAX_LIVE_CALLS / TOKEN_STOP_THRESHOLD | 300 / 200000; 기존 호출 예산 |
| TEAM_API_KEY / CORS_ORIGINS | 기존 팀 인증·CORS 설정 |

실제 실행은 .env의 지급받은 키·주소·모델을 확인하고 MOCK_MODE=false로 변경한 뒤 재시작하세요. 비용 발생 가능성을 확인한 뒤 호출하세요. /health는 설정 여부만 보여주며 실제 연결 성공을 보장하지 않습니다. 실제 .env와 API 키는 Git·로그·응답에 넣지 않습니다.

전사 지시문, 원문 언어 유지(preserve_language=true), 출력 토큰, JSON 스키마와 모의 결과는 `tasks.json → image_text`에서 수정합니다. 라우터는 app/vision.py, 추출 서비스는 app/image_service.py, 응답 모델은 app/image_schemas.py, 검증·전처리는 app/images.py, 제공자 호출은 기존 app/provider.py, 환경 설정은 app/settings.py입니다. 백엔드에서 `await extract_image_text(engine, validated_data_uri)`로 같은 결과를 재사용할 수 있습니다. 응답 필드를 바꾸면 다른 담당자와 계약도 맞추세요.

### 자동 검증

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Python 3.12에서 기존 테스트와 이미지 테스트 총 49개가 통과했습니다. 실제 Uvicorn 서버의 /docs 접근과 multipart 이미지 업로드·모의 JSON 반환도 확인했습니다. tests/test_image_api.py는 지원 이미지, 원문·줄바꿈 반환, 글자 없음(제공자 대역), 모의 표시, 기존 기본 task, /docs 요청 스키마, 잘못된 이미지, 용량·픽셀 제한, HTTP 대역의 인증·호출 제한·타임아웃·연결·잘못된 응답을 검사합니다. 외부 AI 호출 및 실제 추출 정확도는 검증하지 않았습니다. 새 라이브러리나 공통 의존성 변경은 없습니다.

## 바로 실행

Python 3.11 이상이 필요합니다. 프로젝트 폴더에서 실행하세요.

```sh
sh scripts/start.sh
```

팀원이 새로 받는 경우에는 아래 순서로 실행합니다.

```sh
git clone https://github.com/LimitHackathon02/LH02_Backend.git
cd LH02_Backend
sh scripts/start.sh
```

`scripts/start.sh`가 `.venv`를 만들고, `requirements.txt`를 설치하고, `.env.example`을 `.env`로 복사합니다. 즉 README를 보고 위 명령을 실행하면 기본 모의 실행 환경은 자동으로 준비됩니다. API 키, 지급된 모델명, 팀별 CORS 주소는 각자 생성된 `.env`에 입력해야 하며 `.env` 파일은 저장소에 올리지 않습니다.

Windows에서는 Git Bash 또는 WSL에서 위 명령을 실행하세요. macOS/Linux 터미널에서는 그대로 실행하면 됩니다. Python이 없거나 Python 3.11 미만이면 먼저 Python을 설치해야 합니다.

브라우저에서 **http://localhost:8000/docs**를 열면 프론트엔드 없이 API를 실행할 수 있습니다. `/api/run` → `Try it out`에서 아래 요청을 넣으세요.

```json
{"task":"summarize","text":"지민이 금요일까지 설문을 모으고 토요일에 발표 자료를 완성한다."}
```

`mock: true`는 연결 확인용 고정 예시입니다. 입력 요약·이미지 분석·답변 품질을 검증한 결과가 아닙니다. 모의 실행에서 `usage`는 0입니다.

## 실제 HyperCLOVA X 연결

1. `.env`에 지급받은 `CLOVA_API_KEY`를 입력합니다.
2. 주최 측 모델·API 주소와 `CLOVA_TEXT_MODEL`, `CLOVA_VISION_MODEL`, `CLOVA_BASE_URL`을 맞춥니다.
3. `MOCK_MODE=false`로 바꾼 뒤 서버를 종료하고 다시 실행합니다.
4. `/health`에서 `mock: false`, `api_key_configured: true`를 확인합니다. 이는 설정 확인이며 실제 연결 성공 여부는 `/api/run`에서 확인합니다.

일반 CLOVA Studio v3 REST 형식과 `Authorization: Bearer` 인증을 구현했습니다. 공식 문서는 [텍스트·이미지 API](https://api.ncloud-docs.com/docs/clovastudio-chatcompletionsv3), [API 개요](https://api.ncloud-docs.com/docs/ai-naver-clovastudio-summary)를 참고하세요. 기본 텍스트 모델은 `HCX-DASH-002`, 이미지 모델은 `HCX-005`입니다. **대회 전용 프록시, 구형 이중 키 인증, 추론 전용 모델은 API 형식이 다를 수 있어 `app/provider.py`와 요청 파라미터 확인이 필요합니다.** 모델 이름만 바꾸면 모든 API가 호환되는 것은 아닙니다.

## 기능

| API | 용도 | 주제가 바뀌면 바꿀 부분 |
|---|---|---|
| `GET /api/tasks` | 작업·예제·결과 형식 조회 | `tasks.json` |
| `POST /api/run` | 요약, 분류, 추출, 문장 변환, 계획, 채팅 | task, text, context |
| `POST /api/vision` | 이미지와 질문 분석 | 파일, question, task |
| `POST /api/documents` | 텍스트 자료 저장 | title, text |
| `POST /api/documents/upload` | UTF-8 TXT/MD 파일 저장 | file |
| `GET /api/documents` | 문서 ID 목록 | — |
| `DELETE /api/documents/{id}` | 문서 삭제 | 문서 ID |
| `POST /api/ask` | 검색된 문서 조각을 근거로 답변 생성 | question, document_ids |
| `GET /api/usage` | 호출 시도 수·누적 토큰·사용량 미확인 건 조회 | `.env` 한도 |

`/api/run`의 결과는 `output`에 들어갑니다. JSON 작업은 서버가 스키마를 검사한 뒤 반환합니다. 모델 자체의 Structured Outputs 기능에 의존하지 않는 방식이라 잘못된 JSON이면 502 오류가 날 수 있습니다. 조용히 재호출하거나 임의로 채워 넣지 않습니다.

`history`는 최대 8개, 각 2,000자입니다. 채팅에 사용하려면 `[{"role":"user","content":"..."},{"role":"assistant","content":"..."}]` 형식으로 전달합니다. 대화는 서버가 자동 저장하지 않습니다. 주제를 바꾸면 history도 비우세요.

이미지는 10MB 이하 PNG/JPEG/WEBP/BMP를 지원합니다. 한 요청에 1장, 긴 변 최대 1,280px로 축소하고 JPEG로 변환하며 비율이 5:1을 넘으면 흰 여백을 추가합니다. 원본 메타데이터는 전송하지 않습니다. 작은 글자의 인식 정확도는 축소로 낮아질 수 있습니다. 이미지 이해 결과는 전용 OCR의 정확도 보장이 아닙니다.

문서는 10만 자 이하, 전체 1,000개 조각까지 저장합니다. 검색은 한국어 문자 2-gram 유사도이며 **의미 검색·인터넷 검색을 하지 않습니다**. 동의어·짧은 질문에는 관련 자료를 놓칠 수 있습니다. 답변의 `citations`는 서버가 제공한 조각 ID인지 검사합니다. `sources`는 검색 후보이고, 그 중 `citations`에 든 항목이 모델이 사용했다고 표시한 근거입니다. 인용 ID 검사는 답변 사실성까지 보장하지 않습니다. PDF는 텍스트를 복사해서 `/api/documents`에 넣거나 필요한 페이지를 이미지로 분석하세요.

## 주제 공개 후 수정: 코드 대신 작업 설정

`tasks.json`에서 기존 작업을 복사해 작업 ID를 만들고 다음 항목을 바꾸세요.

- `description`: 팀원에게 보여줄 기능 설명
- `prompt`: 누구를 돕고 어떤 결과를 만들 것인지
- `schema`: 프론트엔드에서 쓸 JSON 필드와 필수 항목
- `mock_output`: 그 스키마에 맞는 연습용 응답
- `example_input`: 연습 입력
- `max_tokens`: 출력 길이, 1~4,096
- `temperature`: 0이면 동일 요청 캐시 사용 가능, 창작은 0.3~0.7 고려

수정 후 서버를 재시작합니다. 스키마나 mock_output이 잘못되면 시작 시 오류가 나므로 실제 토큰을 쓰기 전에 확인할 수 있습니다. 모든 작업은 동일한 `/api/run`과 `/api/vision`에서 사용할 수 있습니다. 이미지가 필요하면 `/api/vision`에 task를 전달하면 됩니다.

예: 교육 주제 → `extract`를 학습 개념 추출로 바꾸고 결과 필드를 `concepts`, `questions`로 변경. 생활 주제 → `image_analyze`를 안내문·분리배출·물품 사진 분석으로 변경. 행정 주제 → 문서 자료를 등록한 뒤 `/api/ask`로 신청 조건 설명. 실제 제도·시간·가격은 주최 측 또는 제공 자료로 채워야 합니다.

## 팀 프론트엔드 연결

`examples/frontend.js`를 복사해 사용하세요. CLOVA API 키는 서버 `.env`에만 저장합니다. 프론트엔드 주소는 `.env`의 `CORS_ORIGINS`에 추가합니다. 다른 기기에서 접근하려면 아래 명령으로 실행하고 `BASE`를 서버 컴퓨터의 LAN IP로 변경하세요.

```sh
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

외부에 공유할 때는 `TEAM_API_KEY`를 설정하고 요청마다 `X-Team-Key`를 보냅니다. 이는 팀 단위 공유 키이며 사용자별 계정·데이터 격리는 없습니다. 모든 팀 요청은 같은 문서 저장소와 토큰 한도를 사용합니다. `.env`, `data/`, `.venv/`는 Git 제외 대상입니다.

## 토큰 관리와 검증 범위

`temperature=0`의 동일 요청은 기본 1시간 캐시합니다. 캐시 응답은 `cached: true`, 이번 호출의 `usage: 0`입니다. `use_cache: false`로 끌 수 있습니다. 모의 실행 캐시는 실제 실행 캐시와 분리되어 있습니다. 공급자가 반환한 입력·출력 토큰은 SQLite에 누적하며 서버 재시작 후에도 남습니다. 가격은 모델별로 달라 원화 비용은 임의 계산하지 않습니다.

`MAX_LIVE_CALLS`는 실패를 포함한 실제 호출 시도 횟수 제한입니다. `TOKEN_STOP_THRESHOLD`는 확인된 누적 토큰이 기준에 도달하면 다음 호출을 막습니다. **실제 결제 한도를 보장하는 장치는 아닙니다.** 마지막 한 번의 응답으로 기준을 초과할 수 있고 타임아웃·오류에서 사용량을 알 수 없으면 `unknown_usage_calls`에 표시합니다. 공급자 콘솔의 실제 사용량도 확인하세요. 자동 재시도는 없습니다.

해커톤 규모의 단일 서버·단일 프로세스를 기준으로 했습니다. `--workers`를 늘리면 프로세스 간 예산 확인과 중복 호출 방지가 보장되지 않습니다. 캐시에는 생성 결과, DB에는 입력한 문서와 토큰 사용량이 저장됩니다. 문서를 지워도 기존 생성 결과 캐시는 TTL까지 남을 수 있습니다.

```sh
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

테스트는 모의 실행과 공급자 응답 대역으로 수행하므로 실제 API 권한·요금·모델 품질은 별도 실호출 확인 대상입니다. 설치 버전은 `requirements.lock.txt`에 기록합니다. 같은 버전으로 재설치하려면 `pip install -r requirements.lock.txt`를 사용하세요.

## 행사 전에 챙길 것

사전 준비 금지에 대한 사용자 설명을 기준으로, 코드 반입을 전제로 삼지 않습니다. 학습 자체도 허용 범위인지 행사 규정에 맞게 판단하세요. 허용된 연습 범위에서 API 연결 흐름을 익히고, 행사장에서 제공된 모델로 텍스트 1회·이미지 1회 실호출을 확인하면 오류를 일찍 발견할 수 있습니다. 최종 데모는 입력 → 분석 결과 → 사용자가 할 행동의 한 흐름으로 좁히세요.
