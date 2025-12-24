# AI 해커톤 : 🍳 오늘 뭐먹지

> 요리 쇼츠를 ‘보는 콘텐츠’에서 ‘실제로 완성하는 한 끼’로 바꿔주는 AI 요리 파트너

- Hackathon Period: 2025.12.17 ~ 2025.12.19 (3 days)
- Team: 11팀 (총 6명)

## 📌 프로젝트 소개

- YouTube 등 영상 플랫폼 요리 쇼츠 URL 하나만으로<br>
  레시피 자동 추출 → 단계별 타임라인 → 실시간 AI 코칭까지 제공하는
  대화형 AI 요리 도우미 서비스입니다.

## 🧠 문제 정의 (주제 선택 이유)

최근 외식 물가 상승으로
집에서 직접 요리해 식사를 해결하는 사람들이 늘어나면서,
요리 쇼츠 콘텐츠 역시 빠르게 증가하고 있습니다.

하지만 막상 요리를 따라 해보면,

- 쇼츠 특성상 영상 속도가 빠르고

- 필요한 장면을 앞뒤로 반복해 확인해야 하며

- 요리 중 지금 상태가 맞는지 판단하기 어렵습니다

즉,
요리를 ‘보여주는 콘텐츠’는 충분하지만,
요리 중 실시간으로 도와주는 서비스는 부족한 상황입니다.

저희는 이러한 불편함에 주목해,
영상 기반 요리 콘텐츠를 실제로 따라 할 수 있는 레시피 경험으로 전환하고자
이번 주제를 선택했습니다.

## 🌐 시스템 아키텍처

- 본 서비스는 AI 해커톤 환경에서 아이디어 검증과 빠른 MVP 완성을 최우선 목표로 설계했습니다.

```
[ User ]
    |
    v
[ External Domain ]
    |
    v
+-------------------------------------------------------------+
|                 EC2 (t3.large · Public Subnet)              |
|                                                             |
|  [ Nginx ]                                                   |
|  - Reverse Proxy                                            |
|  - React Static Assets                                      |
|       |                                                     |
|       v                                                     |
|  [ Spring Boot API ]                                        |
|       |                                                     |
|       +----------------->  [ MySQL ]                        |
|       |                |
|       |                                                     |
|       +----------------->  [ FastAPI ]                      |
|                                                             |
+-------------------------------------------------------------+
                                |
                                v
                          [ AWS S3 ]

```

## 🛠 트러블슈팅

1. YouTube 다운로드 제한 이슈 (AWS 환경)

   - AWS에 배포한 환경에서는 YouTube 정책 및 봇 탐지 제한으로 인해 영상 다운로드가 정상적으로 동작하지 않는 문제가 발생했습니다. 이는 애플리케이션 로직의 문제라기보다는 클라우드 IP 기반 접근 제한에 따른 외부 정책 이슈로 판단하였으며, 실제로 로컬 개발 환경에서는 동일한 로직으로 정상 다운로드가 확인되었습니다. 해커톤 시연의 안정성을 위해, 최종 데모에서는 사전에 준비된 더미 데이터 기반으로 시연을 진행했습니다.

2. FastAPI vs Spring AI

   - 초기에는 Spring AI를 활용한 OpenAI API 호출 구조도 고려했으나, 향후 GPU 서버에 AI 모델을 직접 로딩하여 추론하는 구조로 확장할 가능성을 염두에 두고 기술 스택을 재검토했습니다. GPU 기반 모델 서빙 시 필수적으로 사용되는 라이브러리는 Python 환경에서만 제공되며, Java 기반의 Spring AI로는 이를 직접 활용하기 어렵다는 한계가 있었습니다.
   - 이에 따라, 모델을 직접 서빙하는 구조까지 커버할 수 있는 Python 기반 FastAPI를 AI 서빙 레이어로 선택했습니다. 비록 해커톤 기간 내 GPU 서버를 실제로 사용하지는 못했지만, 향후 확장성을 고려한 아키텍처 선택이었으며, AI 팀 구성원 입장에서도 Spring 대비 FastAPI의 러닝 커브가 낮아 빠른 개발과 협업이 가능하다는 점 역시 중요한 선택 이유였습니다.

3. GPU 인스턴스 할당 제한

   - 초기 설계에서는 GPU 서버를 활용해 AI 모델을 직접 서빙할 계획이었으나, AWS GPU 인스턴스 할당량 승인 지연으로 인해 해커톤 기간 내 GPU 서버를 사용할 수 없었습니다. 이에 따라 모델 연산은 외부 API 기반으로 대체하고, GPU 서버 도입을 전제로 한 아키텍처 설계만 유지한 채 MVP를 완성했습니다.

4. CI/CD 파이프라인 캐싱 최적화
   - 초기 CI/CD 구성에서는 Spring Boot와 FastAPI 빌드가 수행될때 배포 시간이 과도하게 증가하는 문제가 있었습니다. 이를 해결하기 위해 GitHub Actions 워크플로우에서 변경된 디렉토리만 빌드 및 캐싱하도록 개선하여, 불필요한 빌드를 제거하고 배포 시간을 단축했습니다. 이를 통해 해커톤 기간 동안 빠른 수정–배포–검증 사이클을 유지할 수 있었습니다.

## 🚀 주요 기능 요약

### URL입력 및 영상 분석

- YouTube 등 플램폿의 Shorts URL 입력
- STT + LLM 기반으로
  - 재료
  - 조리 순서
  - 단계별 타임라인 자동 추출

### 단계별 타임라인 반복 재생

- 조리 단계별 핵심 장면 스냅샷 제공
- 필요한 구간만 반복 확인 가능

### 대화형 챗봇 인터페이스

- 자연스러운 대화형 UX 제공
- 요리 중 궁금한 점을 질문
- 단계 맥락을 이해한 답변 제공

### 실시간 AI 요리 코칭

- 요리 중 사진 업로드
- AI가 상태를 분석하여 조언 및 다음단계 안내
  - “조금 더 끓이세요”
  - “이제 다음 단계로 가도 됩니다”

## 💻 기술 스택

### AI

- Framework: FastAPI
- Language: Python 3.11
- STT Model: OpenAI Whisper
- LLM / Vision Model: GPT-4o

### Frontend

- Framework: Vite + React (SPA)
- Language: TypeScript
- UI Library: React 18.2.0
- Routing: React Router DOM
- Styling: Tailwind CSS
- HTTP Client: Axios

### Backend

- Framework: Spring Boot 3.5.8
- Language: Java 21
- Database: MySQL

### Infrastructure & Deployment

- Cloud: AWS EC2, S3
- Web Server: Nginx (Reverse Proxy)
- Container: Docker, Docker Compose
- Deployment: Public Domain-based Service Deployment

## 서비스 화면

`메인`
|메인|로그인|회원가입|
|---|---|---|
|![image](https://github.com/user-attachments/assets/10f6c42e-000a-4508-89d8-8ea42f6f58e1)|![image](https://github.com/user-attachments/assets/3c6be183-e53b-438a-8541-3e8760728d4d)|![image](https://github.com/user-attachments/assets/d5345f5f-8f96-49b6-8600-7c93492607a0)|

`분석 과정/결과`
|분석중|분석결과|분석결과 하단 레시피 결과|분석결과 하단 타임라인|
|---|---|---|---|
|![image](https://github.com/user-attachments/assets/ba45b208-edeb-417a-aca2-0845f509b26b)|![image](https://github.com/user-attachments/assets/08360c91-748a-457c-bace-0ec6b85c15fc) |![image](https://github.com/user-attachments/assets/d94981d8-2087-491b-9147-85bb4a311177)| ![image](https://github.com/user-attachments/assets/e5b875f9-2ca1-48e2-9127-abcf85b8af49)|

`챗봇 화면`
|챗봇 입장|대화중1|대화중2|
|---|---|---|
|![image](https://github.com/user-attachments/assets/4e27914f-a298-4c6e-b2e1-c05976f7c8c2)|![image](https://github.com/user-attachments/assets/f980b3e1-14a5-41d7-bb5e-8f4712a5e0cb)|![image](https://github.com/user-attachments/assets/62c36160-5c9e-4c77-ab46-6aef4f32c93e)|

<br/>

## ▶️ 시연 영상

https://github.com/user-attachments/assets/8b81768b-4d50-4f76-8980-eeedd110afbe

## 🎤 발표 자료

[오늘 뭐먹지.pdf](https://drive.google.com/file/d/1_vUDLr6GLhBd0zJu9Y4KY7LVBETA1u39/view?usp=sharing)

## 📝 회고

주제 선정부터 배포까지 48시간이라는 제한된 시간 안에 모든 과정을 완주하는 것은 생각보다 훨씬 어려운 경험이었다. 시간이 부족할수록 개발 주기를 짧게 가져가며 빠르게 검증하는 것이 중요하다는 점을 알고 있었지만, 실제로는 각 단계마다 예상보다 많은 조율과 수정이 필요해 쉽지 않았다.

초기 역할 분담 이후 인프라 및 배포 구조를 설계했으며, AI 해커톤이라는 특성을 고려해 복잡한 인프라 설계보다 빠른 배포와 반복 실험이 가능한 구조를 선택했다. 이에 따라 단일 EC2(t3.large)에 Docker 기반으로 모든 서비스를 구성하는 방식을 채택했고, 이는 MVP를 빠르게 완성하는 데 효과적인 선택이었다.

또한 다른 팀들의 발표와 심사 과정을 지켜보며, 해커톤의 주제 선정은 단순히 “무엇을 개발할 것인가”를 넘어서, 제한된 자원과 시간 안에서 어떤 범위까지를 MVP로 정의할 것인지, 타겟 사용자와 초기 서비스 방향을 어떻게 설정할 것인지에 대한 명확한 기준이 훨씬 중요하다는 점을 깨닫게 되었다. 동일한 설계 선택에 대해서도 서로 다른 관점의 평가가 존재한다는 것을 보며, 하나의 정답보다는 의사결정의 맥락과 근거를 설명하는 힘이 중요하다는 생각이 들었다.
