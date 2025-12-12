# debug_model_scan.py

import os
import re
import inspect
from app.schemas.captcha_submit import CaptchaSubmitRequest

TARGET_CLASS = "CaptchaSubmitRequest"


def scan_python_files(root="."):
    print(f"\n📌 [1] 프로젝트 전체에서 '{TARGET_CLASS}' 정의 검색 중...\n")

    matches = []

    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith(".py"):
                fullpath = os.path.join(dirpath, filename)

                try:
                    with open(fullpath, "r", encoding="utf-8") as f:
                        content = f.read()

                        if re.search(r"class\s+" + TARGET_CLASS, content):
                            matches.append(fullpath)
                except:
                    pass

    if not matches:
        print("❌ 클래스 정의가 발견되지 않음! (중대한 문제)")
    else:
        print("✅ 클래스 정의된 파일들:")
        for m in matches:
            print("   -", m)

    return matches


def check_import_path():
    print("\n📌 [2] FastAPI가 실제로 import 한 모델 경로 확인...\n")

    path = inspect.getfile(CaptchaSubmitRequest)
    print("🔍 실제 import 된 파일 경로:")
    print("   →", path)

    print("\n📌 [3] 모델 필드 출력...")
    print("🔍 CaptchaSubmitRequest.model_fields =")
    print(CaptchaSubmitRequest.model_fields)


if __name__ == "__main__":
    print("🚀 CAPTCHA Submit 모델 디버그 스캔 시작\n")

    scan_python_files("./app")

    check_import_path()

    print("\n🎯 디버그 완료 — 위 출력 내용을 나에게 보내줘!")
