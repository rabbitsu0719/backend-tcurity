# 🛡️ T:CURITY – 2-Phase CAPTCHA Backend

**T:CURITY**는 기존 CAPTCHA의 자동화 취약점을 해결하기 위해  
**행동 기반 검증(Phase A)**과 **인지 + 행동 결합 검증(Phase B)**을 단계적으로 수행하는  
**2-Phase CAPTCHA 서비스의 백엔드 서버**입니다.

본 레포지토리는 **세션 관리, 상태 머신(FSM), 검증 로직, 보안 정책**을 담당합니다.

---

## ✨ Core Features

### 🔹 2-Phase CAPTCHA 구조
- **Phase A (Behavior Filter)**  
  저비용·고속 행동 검증 (절취선 드래그 궤적 분석)
- **Phase B (Cognitive + Action)**  
  Drag & Drop 기반 이미지 분류 검증

➡️ 서버가 위험도를 판단하여 단계적으로 검증 수행

---

### 🔹 Server-Driven Flow (Client-Blind)
- 클라이언트는 **현재 Phase를 알 수 없음**
- 항상 동일한 `/captcha/submit` 엔드포인트만 호출
- 모든 상태 전이는 **서버 FSM**이 관리

➡️ 단계 위조, Phase 스킵, 반복 호출 구조적으로 차단

---

### 🔹 Blind Error Policy
- 모든 실패 응답은 **HTTP 200 OK**
- 실패 원인(정답/행동/상태)을 구분할 수 없음
- 공격자에게 힌트를 제공하지 않음

---

### 🔹 Replay Attack Protection
- 인증 완료 세션은 **1회만 검증 가능**
- `/captcha/verify` 재요청 시 자동 차단

---

## 🔄 CAPTCHA Flow

```text
Session Init
   ↓
PHASE_A (Behavior)
   ↓
PHASE_B (Cognitive + Action)
   ↓
COMPLETED
   ↓
VERIFY (S2S)
   ↓
VERIFIED → Replay 차단
```

---

## 🧠 State Machine (FSM)

```text
INIT
 ↓
PHASE_A
 ↓
PHASE_B
 ↓
COMPLETED
 ↓
VERIFIED
 ↓
(REPLAY) → BLOCKED
```

---

## 📡 API Overview

| Endpoint | Method | Description |
|------|------|------|
| `/session/init` | POST | 인증 세션 생성 |
| `/captcha/request` | GET | CAPTCHA 문제 요청 |
| `/captcha/submit` | POST | Phase A / B 통합 제출 |
| `/captcha/verify` | POST | 최종 서버 간(S2S) 검증 |

> 📌 클라이언트는 Phase 상태를 알 수 없으며  
> 서버가 세션 상태에 따라 자동 분기합니다.

---

## 🛠 Tech Stack

### Backend
- **FastAPI**
- Python 3.11
- In-Memory Session Store (TTL 기반)
- Finite State Machine (FSM)

### AI / Inference (연동)
- Phase A: 행동 궤적 기반 이상 탐지
- Phase B: 이미지 분류 + Drag & Drop 검증
- GPU Inference Server 분리 운영

### Security
- Blind Error Policy
- Replay Attack Block
- Server-Driven Verification
- Client-Blind Phase Design

---

## 📂 Project Structure

```text
backend-tcurity/
 ├─ app/
 │  ├─ endpoints/
 │  │  ├─ session_endpoints.py
 │  │  ├─ captcha_endpoints.py
 │  │  └─ verify_endpoints.py
 │  ├─ services/
 │  │  ├─ phase_a_service.py
 │  │  └─ phase_b_service.py
 │  ├─ core/
 │  │  ├─ state_machine.py
 │  │  └─ session_store.py
 │  └─ utils/
 └─ main.py
```

---

## 🚀 Why T:CURITY?

| 기존 CAPTCHA | T:CURITY |
|-------------|----------|
| 정답 중심 | 행동 + 인지 결합 |
| 클라이언트 단계 인지 | 서버 완전 통제 |
| 반복 공격 가능 | Replay 차단 |
| 실패 원인 노출 | Blind Error |

---

## 👥 Team Project

**T:CURITY**는  
SniperFactory × KakaoCloud AIaaS Bootcamp 과정에서  
**실제 서비스 환경을 가정하여 설계·구현 중인 팀 프로젝트**입니다.

---
