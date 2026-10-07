# LH02 이미지 텍스트 추출 API — 해커톤 실전 사용 가이드

## 1. 이 기능으로 할 수 있는 일

이미지 한 장에서 글자를 읽어 원문 텍스트를 반환한다. 공지, 안내문, 메뉴판, 영수증 등 글자가 담긴 이미지를 입력으로 사용할 수 있다. 인식 결과는 원본과 대조해야 하며 손글씨·작은 글자·복잡한 배치의 정확도는 별도 확인이 필요하다.

이 문서의 주 대상은 `task=image_text`다. 일정·장소 추출, 요약, 번역, 지도 표시까지 자동 수행하는 기능은 아니다. 그런 처리는 추출된 텍스트를 다음 기능에 전달해 구현한다.

예: 공지 사진 → 이 API로 원문 추출 → 텍스트 담당 API로 날짜·장소 추출 → 지도 기능으로 장소 표시.

## 2. 현재 준비된 상태와 위치

| 항목 | 내용 |
|---|---|
| 팀 원본 | LimitHackathon02/LH02_backend |
| 내 Fork | kkkangji/image-ai-frontend-starter |
| 로컬 작업 폴더 | C:\limit_ai\LH02_backend_work |
| 기능 브랜치 | feature/image-api |
| API | POST /api/vision |
| 추출 작업 | task=image_text |
| 결과 | output.text |
| 로컬 서버 | http://127.0.0.1:8081 |

대화에서 확인한 상태: 자동 테스트 51개 통과는 로컬 Codex의 보고이며, 영어 이미지의 실제 호출 응답에서 mock=false, cached=false와 추출 텍스트를 확인했다. 한글 정확도와 다양한 이미지의 성능은 별도 확인해야 한다. 사용자가 Commit을 완료했다고 했으며 Push·PR·Merge 완료 여부는 확인되지 않았다. 현재 저장소 코드를 직접 재검토한 문서는 아니므로 최종 README와 실제 API 스키마를 함께 확인한다.

## 3. 내일 처음 할 일

1. GitHub Desktop에서 내 Fork와 feature/image-api 브랜치를 선택한다.
2. 아직 Push하지 않았다면 Publish branch 또는 Push origin을 눌러 원격에 저장한다.
3. 팀 통합 담당에게 이 브랜치를 공유한다. 원본에 넣을 때는 원본 main ← 내 Fork feature/image-api 방향으로 PR을 보내고 검토 후 Merge한다.
4. 통합된 프로젝트에서 .env를 별도로 설정하고 서버를 켠다. .env는 Git으로 전달되지 않는다.
5. Swagger에서 실제 이미지 한 장으로 동작을 확인한 다음 프론트를 연결한다.

원본에 이미 같은 API가 있으므로 팀원이 파일을 통째로 덮어쓰지 않게 한다. Git PR로 통합하고 다른 팀원의 변경과 충돌을 해결한다. 미완성 작업이 있는 상태에서 강제 초기화하지 않는다.

## 4. 실행 방법 — 내 Windows 컴퓨터

VS Code에서 C:\limit_ai\LH02_backend_work를 열고 터미널을 실행한다.

기존 가상환경이 준비된 경우:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8081
```

`Uvicorn running on http://127.0.0.1:8081`이 나오면 실행 중이다. 터미널을 유지한다. Ctrl+C로 종료한다. 이 컴퓨터에서는 8000 포트에 Windows 10013 오류가 발생했으므로 8081을 사용한다.

다른 팀원의 컴퓨터에서는 저장소 README의 Python 버전과 설치 명령을 따른다. .venv 폴더를 복사하지 않고 각자 생성한다. 의존성 파일 이름과 설치 방식은 최종 저장소 README를 기준으로 한다.

### 실제 AI 설정

프로젝트 최상위 .env에 다음 항목을 설정한다. 기존 다른 항목은 보존한다.

```dotenv
MOCK_MODE=false
CLOVA_API_KEY=여기에_로컬에서_새_API_키_입력
CLOVA_BASE_URL=https://clovastudio.stream.ntruss.com
CLOVA_VISION_MODEL=HCX-005
CLOVA_TIMEOUT_SECONDS=60
```

.env가 없으면 .env.example을 복사한다.

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

키는 CLOVA Studio에서 발급받은 키를 사용한다. 화면에 노출됐던 키는 삭제하고 새 키를 사용한다. .env와 실제 키는 커밋하지 않고 프론트에 넣지 않는다. .env.example은 키 값 없이 공유한다. 설정 변경 후 서버를 재시작한다. 실제 API 호출은 비용·크레딧을 사용하므로 팀의 사용 가능 범위를 확인한다.

## 5. Swagger에서 바로 확인하기

1. http://127.0.0.1:8081/health 접속: mock=false, api_key_configured=true를 확인한다. 이는 설정 상태이며 키 유효성이나 호출 성공을 보장하지는 않는다.
2. http://127.0.0.1:8081/docs 접속.
3. POST /api/vision 펼치기 → Try it out.
4. file에 글자가 선명한 이미지 선택.
5. task를 기본 image_analyze에서 image_text로 변경.
6. question은 기본값 유지. image_text에서 질문이 어떻게 적용되는지는 최종 구현을 따른다.
7. use_cache=false로 지정하고 Execute.
8. Server response의 Code와 Response body 확인.

성공 기준: HTTP 200, task=image_text, mock=false, output.text에 실제 이미지의 글자가 반환됨. cached=false는 새 처리 결과임을 나타낸다. 모의 모드의 [MOCK] 텍스트는 실제 인식 성공이 아니다. 아래 Responses의 422 예시는 오류 문서이며 실제 Server response와 구분한다.

## 6. 프론트 담당에게 전달할 요청·응답 계약

| 항목 | 값 |
|---|---|
| 메서드 | POST |
| 경로 | /api/vision |
| 요청 형식 | multipart/form-data |
| file | 이미지 파일 한 장 |
| task | image_text |
| question | 기존 기본값 사용 또는 구현에 맞는 선택적 문자열 |
| use_cache | 새 인식 확인 시 false |
| 결과 위치 | 응답 JSON의 output.text |

구현 보고 기준 파일 제한은 10MiB(10 × 1024 × 1024바이트), 2천만 픽셀이다. PNG/JPEG/WEBP/BMP가 기존 지원 형식으로 안내됐으며 최종 README·파일 검사 코드에서 지원 목록을 확인한다. 확장자만 바꾼 파일, 손상된 이미지는 허용되지 않는다.

### 실제 응답의 형태

```json
{
  "task": "image_text",
  "output": { "text": "멘토링 안내\n10월 23일 오후 2시\n준비물: 노트북" },
  "model": "HCX-005",
  "mock": false,
  "cached": false,
  "finish_reason": "stop",
  "usage": { "prompt_tokens": 1605, "completion_tokens": 95, "total_tokens": 1700 }
}
```

텍스트와 토큰 수는 설명용 예시다. 실제 값은 이미지·요청마다 달라진다. JSON의 \n은 줄바꿈이다. 글자가 없으면 output.text가 빈 문자열일 수 있으며 그 경우 사용자에게 글자를 찾지 못했다고 안내한다.

### 브라우저 JavaScript 연결 예시

```javascript
export async function extractImageText(file, backendBaseUrl) {
  const form = new FormData();
  form.append("file", file);
  form.append("task", "image_text");
  form.append("use_cache", "false");

  const base = backendBaseUrl.replace(/\/$/, "");
  const response = await fetch(`${base}/api/vision`, {
    method: "POST",
    body: form,
  });

  if (!response.ok) {
    throw new Error(`이미지 텍스트 추출 실패 (${response.status})`);
  }
  const result = await response.json();
  if (result.mock) {
    throw new Error("백엔드가 모의 모드입니다. 실제 AI 설정을 확인하세요.");
  }
  if (typeof result.output?.text !== "string") {
    throw new Error("응답에 추출 텍스트가 없습니다.");
  }
  return result.output.text;
}

// file은 파일 선택 입력에서 가져온 File 객체다.
const text = await extractImageText(file, "http://127.0.0.1:8081");
// text를 결과 화면에 표시하거나 팀의 텍스트 처리 함수에 전달한다.
```

FormData 사용 시 Content-Type 헤더를 직접 지정하지 않는다. 브라우저가 파일 전송에 필요한 boundary까지 설정한다. 클로바 키를 이 코드에 넣지 않는다. 위 코드는 연결 예시이며 최종 프론트에서 별도 실행 검증이 필요하다.

프론트와 백엔드 주소가 다르면 백엔드 CORS 설정에 실제 프론트 origin을 허용해야 한다. 예를 들어 http://localhost:5173과 http://127.0.0.1:5173은 서로 다른 origin이다. 설정 이름·위치는 최종 README나 Codex로 확인한다.

## 7. 주제가 정해지면 어디를 바꾸는가

| 내일 나온 요구 | 할 일 |
|---|---|
| 공지 사진에서 날짜·장소 추출 | image_text 유지 → 반환 원문을 텍스트 처리 기능으로 전달 |
| 메뉴판 사진 번역·추천 | 원문 추출 → 번역·추천 기능으로 전달 |
| 영수증에서 금액 정리 | 원문 추출 → 항목·금액 파싱 기능으로 전달, 숫자 대조 |
| 사진 속 장소를 지도에 표시 | 글자로 적힌 장소면 원문에서 장소 추출 후 지도 검색 |
| 글자가 없는 사진의 사물·장면 이해 | image_text로는 부족함. 기존 image_analyze 또는 별도 분석 task의 지시문·응답을 확인하고 실호출 테스트 |

글자 추출이 필요한 주제라면 API 자체를 다시 만들 필요가 없다. 프론트 문구와 텍스트 후처리를 바꾼다. 추출 목적 자체를 변경해야 한다면 tasks.json과 app/engine.py의 기존 구조를 확인하고 별도 task 추가 여부를 결정한다. 다른 팀이 사용하는 image_text 응답 계약을 임의로 바꾸지 않는다.

## 8. 다른 기능과 연결하는 기준

서로 다른 브라우저 입력을 쓰더라도 원문 문자열을 공통 입력으로 삼는다.

- 직접 입력한 긴 텍스트: 바로 텍스트 처리 기능에 전달.
- 이미지: image_text 호출 후 output.text를 같은 텍스트 처리 기능에 전달.
- 장소 검색: 텍스트 처리 결과에서 장소 이름 또는 주소를 지도 담당에게 전달.

팀과 정할 사항: 텍스트 API의 실제 경로·필드 이름, 장소 출력 형식(이름/주소/좌표), 오류 처리, 요청을 연결하는 담당. 아직 합의되지 않은 API 경로나 함수 이름을 가정해서 붙이지 않는다.

Python에서 HTTP 응답 JSON을 받은 경우에는 다음 문자열을 사용한다.

```python
text = result["output"]["text"]
```

같은 백엔드 안에서 연결한다면 Swagger 페이지를 거치는 것이 아니라 추출 서비스의 실제 함수 반환값을 재사용한다. 함수 이름·서명은 app/image_service.py를 확인한다. 필요 없이 자기 서버를 HTTP로 다시 호출하지 않는다.

## 9. 로컬 주소와 팀 시연

127.0.0.1은 요청을 보내는 기기 자신이다. 팀원의 PC나 휴대폰에 이 주소를 알려주면 내 서버에 연결되지 않는다. 로컬 개발은 각자 서버를 실행하거나 팀이 접근 가능한 서버 주소를 정해야 한다. 배포·공유 주소를 쓰면 프론트의 backendBaseUrl과 CORS를 함께 변경한다. 현재 --host 127.0.0.1 실행은 내 컴퓨터용이며 공개 배포가 아니다.

## 10. 문제 해결표

| 증상 | 먼저 확인할 것 |
|---|---|
| 8000 포트 Windows 10013 | 8081로 실행하고 브라우저 주소도 변경 |
| 접속되지 않음 | 서버 터미널이 살아 있는지, 포트·주소가 맞는지 |
| task=image_analyze 응답 | Swagger의 task를 image_text로 변경 |
| mock=true, [MOCK] 결과 | .env의 MOCK_MODE=false, 저장·재시작, 올바른 폴더와 환경변수 우선순위 |
| 변경 전 결과가 반복됨 | use_cache=false로 테스트 |
| 인증·제공자 오류 | 키 종류·유효 여부, URL·모델 확인. 키는 출력하지 않음 |
| 파일 오류 | 정상 지원 이미지인지, 용량·픽셀 제한 확인 |
| Swagger 성공, 프론트 실패 | API URL·FormData 필드·CORS·브라우저 콘솔 확인 |
| 긴 이미지의 텍스트가 잘림 | finish_reason, 출력 토큰 제한과 이미지 가독성 확인 후 필요한 수정 |

모의 모드로 되돌려 실제 호출 실패를 숨기지 않는다. 오류를 Codex에 전달할 때 HTTP 상태·키를 가린 오류 내용·서버 로그를 전달한다.

## 11. 내일 Codex에게 보낼 연결 프롬프트

```text
현재 feature/image-api에 구현된 이미지 텍스트 추출 기능을 이번 주제에 연결해줘.

주제: [정해진 주제]
입력 이미지: [공지/메뉴판/영수증 등]
추출 원문을 사용할 기능: [텍스트 처리/번역/지도 등]
프론트 프로젝트 위치: [실제 경로]
백엔드 주소: [실제 주소]

기존 POST /api/vision의 task=image_text와 output.text 계약을 재사용해줘.
현재 코드와 README를 먼저 확인하고, 연결할 다른 팀원 API의 실제 요청·응답 형식을 확인해줘.
업로드 → 추출 → 결과 표시 또는 다음 API 전달 흐름을 구현하고 오류·빈 텍스트·로딩을 처리해줘.
클로바 키는 백엔드 .env에서만 관리하고 출력하거나 커밋하지 마.
현재 브랜치의 변경 사항을 보존하고, 자동 push·merge는 하지 마.
```

## 12. 완료 기준

- [ ] 원격 Fork에 커밋을 Push했다.
- [ ] 통합 담당과 브랜치·요청·응답 계약을 공유했다.
- [ ] 실행할 컴퓨터에 .env와 의존성을 준비했다.
- [ ] 실제 모드로 한글·영어 샘플을 확인하고 원본과 대조했다.
- [ ] 프론트에서 output.text를 받아 표시했다.
- [ ] 주제에 맞는 후처리 API와 연결했다.
- [ ] .env·API 키·.venv가 커밋에 포함되지 않았다.

팀 전달용 한 문장: “이미지를 FormData로 POST /api/vision에 보내고 task=image_text를 지정하면 output.text에 원문이 반환됩니다. 실제 클로바 호출은 확인했고, 프론트는 이 문자열을 표시하거나 텍스트 처리 기능에 전달하면 됩니다. 실행 환경에는 API 키를 별도로 설정해야 합니다.”
