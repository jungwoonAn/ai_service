# LLM(OpenAI API)으로 AI Agent 개발

## 1. 프로젝트 개요

본 프로젝트는 **OpenAI API를 활용하여 LLM 기반의 AI Agent를 개발**하는 것을 목적으로 한다.

Flask 기반의 웹 애플리케이션을 구성하고, Chatbot을 중심으로 시스템 역할(System Role), Tool Calling, 보고서 생성 Agent, 경고 Agent 등을 단계적으로 연동한다.

---

## 2. 디렉토리 및 구성 요소

### 2.1 `webapp`

**서버 프로그램(Flask)**

Flask를 기반으로 웹 애플리케이션 서버를 구성한다.

주요 역할:

- Flask 웹 서버 실행
- URL Routing
- HTTP 요청 및 응답 처리
- 웹 애플리케이션의 기본 진입점 제공

```text
webapp
└── Flask Server(app.py)
```

---

### 2.2 `Chatbot`

**Chatbot 설계**

LLM과 사용자 간의 대화를 관리하는 핵심 모듈이다.

주요 역할:

- 대화 Context 관리
- 사용자 메시지 관리
- LLM 요청 및 응답 처리
- Token 사용량 관리
- System Role 적용
- 사용자 응답 처리
- Warning Agent 연동

OpenAI Responses API를 이용하여 LLM과 통신한다.

```text
User
 │
 ▼
Chatbot
 │
 ▼
OpenAI Responses API
 │
 ▼
LLM Response
```

---

### 2.3 `BaseContainer`

**Application Server 구성**

Flask를 기반으로 애플리케이션 서버의 기본 구조를 구성한다.

주요 역할:

- Flask Application 구성
- 웹 화면 제공
- 기본 서버 실행 환경 구성
- 공통 Application 기능 제공

```text
Browser
   │
   ▼
BaseContainer
   │
   └── Flask(application.py)
```

---

### 2.4 `FirstContainer`

**Application + Chatbot 연동**

Flask Application과 Chatbot을 실제로 연결하는 구성 요소이다.

주요 역할:

- 웹 화면에서 사용자 입력 수신
- Chatbot 호출
- LLM 응답 전달
- 사용자와 Chatbot 간 대화 처리

```text
Browser
   │
   ▼
Flask Application
   │
   ▼
Chatbot
   │
   ▼
OpenAI API
```

---

### 2.5 `systemrole_func`

**시스템 역할 및 Tool Calling Function**

Chatbot의 동작 방식을 정의하는 System Role과 Tool Calling에 사용되는 함수를 관리한다.

주요 구성:

- System Role 정의
- Tool Calling Function 정의
- LLM이 사용할 수 있는 기능 정의
- 외부 API 및 데이터 조회 함수 구성

예:

```text
System Role
     │
     ├── Chatbot 역할 정의
     │
     └── Tool Calling
            │
            ├── 날씨 조회
            ├── 환율 조회
            └── 인터넷 검색
```

---

### 2.6 `SystemRoleContainer`

**Chatbot 시스템 역할 설정**

Chatbot이 어떤 역할과 방식으로 응답할지를 정의하는 부분이다.

예를 들어 다음과 같은 역할을 설정할 수 있다.

```text
"당신은 친절한 AI 상담사입니다."
```

또는

```text
"사용자의 질문을 분석하고 필요한 정보를 제공하는 AI 비서입니다."
```

주요 역할:

- System Role 설정
- Chatbot의 성격 및 응답 방식 정의
- LLM에게 전달할 초기 지시사항 구성

---

### 2.7 `ToolCallingContainer`

**Tool Calling 구현**

LLM이 필요한 기능을 판단하고 외부 함수를 호출할 수 있도록 Tool Calling 기능을 구현한다.

주요 역할:

- Tool 정의
- Function Calling 처리
- LLM의 Function Call 분석
- 함수 실행
- 실행 결과를 LLM에 전달
- 최종 응답 생성

전체 흐름:

```text
사용자 질문
    │
    ▼
LLM
    │
    ▼
Function Call 판단
    │
    ▼
Tool Calling
    │
    ▼
Python Function 실행
    │
    ▼
실행 결과
    │
    ▼
LLM
    │
    ▼
최종 응답
```

예:

```text
"서울의 현재 날씨를 알려줘"
          │
          ▼
get_celsius_temperature()
          │
          ▼
"24.8℃"
          │
          ▼
LLM
          │
          ▼
"현재 서울의 기온은 약 24.8℃입니다."
```

---

### 2.8 `AgentContainer`

**AI Agent 구성**

LLM과 Tool Calling을 활용하여 특정 목적을 수행하는 AI Agent를 구현한다.

현재 주요 Agent는 다음과 같다.

#### ① 보고서 생성 Agent

인터넷에서 필요한 자료를 검색하고, 검색 결과를 바탕으로 보고서를 생성한다.

```text
사용자 요청
    │
    ▼
보고서 생성 Agent
    │
    ├── 인터넷 검색
    │
    ├── 자료 수집
    │
    └── 보고서 작성
            │
            ▼
        최종 보고서
```

보고서의 예시 구성:

```text
1. 요약(Executive Summary)
2. 회사 개요
3. 제품·기술 분석
4. 시장·경쟁 분석
5. 재무·성과 분석
6. SWOT 및 리스크·기회
7. 결론 및 제언
8. 참고문헌
```

#### ② 경고 Agent

사용자의 대화 내용을 분석하여 특정 상황이 발생했는지를 판단한다.

현재 다음 두 가지 상황을 검사한다.

- 불쾌한 말
- 모순적인 말

동작 과정:

```text
사용자 메시지
     │
     ▼
Warning Agent
     │
     ▼
대화 내용 분석
     │
 ┌───┴────┐
 │        │
 ▼        ▼
불쾌한 말   모순적인 말
 │        │
 └───┬────┘
     │
     ▼
경고 메시지 생성
```

---

## 3. 전체 구성 관계

각 디렉토리의 역할을 연결하면 다음과 같다.

```text
┌─────────────────────────────┐
│          webapp             │
│       Flask Server          │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       BaseContainer         │
│  Flask + Web Application    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│      FirstContainer         │
│   Application + Chatbot     │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│          Chatbot            │
│     대화 및 LLM 관리        │
└───────┬───────────┬─────────┘
        │           │
        ▼           ▼
┌──────────────┐ ┌──────────────────┐
│SystemRole    │ │ ToolCalling      │
│Container     │ │ Container        │
└──────────────┘ └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │  AgentContainer  │
                  │                  │
                  │  ├─ 보고서 Agent │
                  │  └─ 경고 Agent   │
                  └──────────────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ OpenAI API       │
                  │ Responses API    │
                  └──────────────────┘
```

---

## 4. 디렉토리 역할 요약

| 디렉토리 | 주요 역할 |
|---|---|
| `webapp` | Flask 서버 프로그램 |
| `Chatbot` | Chatbot 설계 및 대화 관리 |
| `BaseContainer` | Flask + 화면 기반 Application Server |
| `FirstContainer` | Flask Application과 Chatbot 연동 |
| `systemrole_func` | System Role 및 Tool Calling Function 정의 |
| `SystemRoleContainer` | Chatbot의 시스템 역할 설정 |
| `ToolCallingContainer` | LLM Tool Calling 구현 |
| `AgentContainer` | 목적별 AI Agent 구현 |
| `AgentContainer/보고서 Agent` | 인터넷 검색 및 보고서 생성 |
| `AgentContainer/경고 Agent` | 불쾌한 말 및 모순적인 말 탐지 |

---

## 5. 핵심 기술

본 프로젝트에서는 다음 기술을 활용한다.

- **Python**
- **Flask**
- **OpenAI API**
- **OpenAI Responses API**
- **LLM**
- **Tool Calling**
- **AI Agent**
- **인터넷 검색 API**
- **Token 관리**
- **대화 Context 관리**

---

## 6. 프로젝트 핵심 흐름

최종적으로 사용자의 요청은 다음과 같은 구조로 처리된다.

```text
사용자
  │
  ▼
Flask Web Application
  │
  ▼
Chatbot
  │
  ├──────────────► System Role
  │
  ├──────────────► Tool Calling
  │                    │
  │                    ▼
  │               외부 Function
  │
  └──────────────► AI Agent
                       │
                ┌──────┴──────┐
                ▼             ▼
            보고서 Agent    경고 Agent
                │             │
                └──────┬──────┘
                       ▼
                  OpenAI LLM
                       │
                       ▼
                    응답
                       │
                       ▼
                    사용자
```

본 프로젝트는 단순한 LLM 호출에서 시작하여 **Chatbot → System Role → Tool Calling → AI Agent**로 기능을 확장하는 구조로 설계되었다.
