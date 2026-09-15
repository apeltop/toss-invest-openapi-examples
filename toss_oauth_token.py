#!/usr/bin/env python3
"""토스증권 Open API OAuth2 액세스 토큰 발급 스크립트.

사용법:
  python3 toss_oauth_token.py

같은 폴더의 .env 파일에 TOSS_CLIENT_ID와 TOSS_CLIENT_SECRET을 입력하면
자동으로 읽습니다. 환경 변수가 있으면 .env 값보다 우선합니다.

토큰은 화면에만 출력하며 파일에 저장하지 않습니다.
"""

import getpass
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


TOKEN_URL = "https://openapi.tossinvest.com/oauth2/token"
ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def load_dotenv(path: str) -> None:
    """필요한 최소 범위의 .env 파일을 읽어, 아직 없는 환경 변수만 설정한다."""
    if not os.path.isfile(path):
        return

    with open(path, encoding="utf-8") as dotenv_file:
        for line_number, raw_line in enumerate(dotenv_file, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].lstrip()
            if "=" not in line:
                raise ValueError(f".env {line_number}번째 줄의 형식이 올바르지 않습니다.")

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if not key:
                raise ValueError(f".env {line_number}번째 줄의 키가 비어 있습니다.")
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '\"'}:
                value = value[1:-1]
            os.environ.setdefault(key, value)


def read_value(env_name: str, prompt: str, *, secret: bool = False) -> str:
    """환경 변수를 우선 사용하고, 없으면 터미널에서 안전하게 입력받는다."""
    value = os.environ.get(env_name)
    if value:
        return value

    reader = getpass.getpass if secret else input
    value = reader(prompt).strip()
    if not value:
        raise ValueError(f"{env_name} 값이 필요합니다.")
    return value


def error_body(error: HTTPError) -> str:
    try:
        body = error.read().decode("utf-8")
        parsed = json.loads(body)
        return json.dumps(parsed, ensure_ascii=False, indent=2)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "응답 본문을 읽을 수 없습니다."


def issue_token(client_id: str, client_secret: str) -> dict:
    payload = urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    ).encode("utf-8")
    request = Request(
        TOKEN_URL,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    try:
        load_dotenv(ENV_FILE)
        client_id = read_value("TOSS_CLIENT_ID", "토스 Client ID: ")
        client_secret = read_value(
            "TOSS_CLIENT_SECRET", "토스 Client Secret (입력 내용 숨김): ", secret=True
        )
        result = issue_token(client_id, client_secret)
    except ValueError as error:
        print(f"입력 오류: {error}", file=sys.stderr)
        return 2
    except HTTPError as error:
        print(f"토큰 발급 실패 (HTTP {error.code}):\n{error_body(error)}", file=sys.stderr)
        if error.code == 403:
            print("허용 IP 설정을 토스증권 WTS의 Open API 메뉴에서 확인하세요.", file=sys.stderr)
        return 1
    except URLError as error:
        print(f"네트워크 오류: {error.reason}", file=sys.stderr)
        return 1
    except json.JSONDecodeError:
        print("토스증권 서버가 JSON이 아닌 응답을 반환했습니다.", file=sys.stderr)
        return 1

    access_token = result.get("access_token")
    if not access_token:
        print("응답에 access_token이 없습니다:\n" + json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    expires_in = result.get("expires_in")
    print("토큰 발급 성공")
    print(f"token_type: {result.get('token_type', 'Bearer')}")
    print(f"access_token: {access_token}")
    if isinstance(expires_in, int):
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        print(f"expires_in: {expires_in}초")
        print(f"expires_at_utc: {expires_at.isoformat()}")
    print("\n다른 API 호출 헤더: Authorization: Bearer <access_token>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
