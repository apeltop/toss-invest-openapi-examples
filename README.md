# 토스증권 Open API OAuth 토큰 발급 예제

토스증권 Open API의 OAuth2 client_credentials 방식으로 액세스 토큰을 발급받는, 외부 패키지 없는 Python 예제입니다.

## 준비물

- Python 3
- 토스증권 Open API 앱의 Client ID와 Client Secret
- API 사용이 허용된 IP 설정

## 실행

    git clone https://github.com/apeltop/toss-invest-oauth-token-example.git
    cd toss-invest-oauth-token-example
    cp .env.example .env

.env를 열어 본인의 값을 입력합니다.

    TOSS_CLIENT_ID=본인의_Client_ID
    TOSS_CLIENT_SECRET=본인의_Client_Secret

그 다음 실행합니다.

    python3 toss_oauth_token.py

성공하면 화면에 액세스 토큰과 만료 정보가 표시됩니다. 다른 API 요청에는 다음 헤더를 사용합니다.

    Authorization: Bearer <access_token>

## 보안 주의사항

- .env에는 실제 Client Secret을 넣으므로 절대 GitHub에 올리지 마세요. 이 저장소의 .gitignore가 이를 제외합니다.
- 발급된 access_token도 비밀값입니다. 캡처, 로그, 커밋, 질문 글에 포함하지 마세요.
- 이 스크립트는 토큰을 파일에 저장하지 않고 터미널에만 출력합니다.
- 환경 변수 TOSS_CLIENT_ID, TOSS_CLIENT_SECRET가 있으면 .env보다 우선합니다.

## 문제 해결

- HTTP 403: 토스증권 WTS의 Open API 메뉴에서 허용 IP 설정을 확인하세요.
- 입력 오류: .env의 키=값 형식을 확인하세요.
- 네트워크 오류: 인터넷 연결과 API 주소 접근 가능 여부를 확인하세요.

## 라이선스

[MIT License](LICENSE)로 제공됩니다.
