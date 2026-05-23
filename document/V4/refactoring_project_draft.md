
---

# Stock_Program_V4 리팩토링 프로젝트 계획서

## 1. 프로젝트 개요 및 목표

* **목표:** 기존 개별 종목 스캔 로직을 고도화하여 '전일 시장 주도 섹터 및 컨텍스트'를 분석하는 시스템으로 개편하며, 레거시 코드의 구조적 결함을 해결하여 유지보수성과 확장성을 극대화함.
* **타임라인:** 1개월
* **기술 스택:** Python, Streamlit, KIS API

---

## 2. 소프트웨어 공학 기반 설계 및 방법론 (설계 지침)

### A. 프로세스 모델 및 방법론 설계

* **프로세스 모델: 반복적 애자일(Iterative Agile) 모델**
* **선정 이유:** 1개월이라는 짧은 기간 내에 API 연동, 로직 분리, UI 개편을 모두 완수해야 합니다. 따라서 전체 시스템을 한 번에 구축하는 폭포수 모델 대신, 핵심 뼈대(인증 및 데이터 수집)를 먼저 구축하고 분석 알고리즘(P1, P2 등)을 점진적으로 붙여나가는 1주 단위의 스프린트(Sprint) 방식이 적합합니다.


* **적용 방법론: AI-TDD (테스트 주도 프롬프팅) 및 Context-First Development**
* **선정 이유:** 레거시 코드의 가장 큰 문제는 로직 검증이 불가능하다는 점입니다. 비즈니스 로직(StockStrategy)을 다시 작성할 때, AI에게 먼저 `pytest` 기반의 단위 테스트 코드를 작성하게 한 뒤(AI-TDD), 이를 통과하는 순수 함수(Pure Function) 로직을 짜도록 강제하여 신뢰성을 확보합니다.



### B. 아키텍처 및 디자인 패턴 선정

* **매크로 아키텍처: 엄격한 MVC (Model-View-Controller) 아키텍처**
* **문제점:** 현재 `app.py`에 UI 렌더링, 데이터 포맷팅, 로직 실행이 심각하게 혼재되어 있습니다.
* **해결책:** * `Model`: KIS API 통신 및 데이터 전처리 (`DataFetcher`)
* `View`: Streamlit 기반의 순수 UI 렌더링 (`app.py`)
* `Controller`: 다중 스캔 및 스레딩을 관리하는 조정자 (`MarketScanner`)




* **마이크로 디자인 패턴 (GoF)**
* **전략 패턴 (Strategy Pattern):** `StockStrategy` 클래스 내에 하드코딩된 P1, P2, Sniper 로직을 분리합니다. `SectorAnalysisStrategy`라는 인터페이스를 만들고 각 분석 알고리즘이 이를 상속받게 하여, 새로운 분석 지표 추가 시 기존 코드를 수정하지 않도록 개방-폐쇄 원칙(OCP)을 준수합니다.
* **싱글톤 패턴 (Singleton Pattern):** KIS API의 인증 토큰 관리 객체에 적용하여, 불필요한 API 중복 호출을 막고 전역적으로 단일한 인증 상태를 유지합니다.
* **의존성 주입 (Dependency Injection):** 하위 모듈이 `KisClient`를 직접 생성하는 문제(DIP 위배)를 해결하기 위해, Controller가 생성된 API 클라이언트 객체를 주입(Inject)해주는 방식을 채택합니다.



### C. 요구사항 분할(PBS) 및 모델링 전략

**[원자적 단위의 PBS (Prompt Breakdown Structure)]**
전체 시스템을 AI가 독립적으로 이해하고 코딩할 수 있는 5단계로 분할합니다.

* **PBS-1 [Infrastructure]:** KIS API 통신 모듈 및 토큰 관리 객체 (Singleton 적용)
* **PBS-2 [Data Layer]:** JSON 파싱 및 Pandas 지표 계산 모듈 (순수 함수 형태로 SRP 준수)
* **PBS-3 [Business Logic]:** 주도주 및 섹터 판별 알고리즘 (Strategy 패턴 적용, AI-TDD로 검증)
* **PBS-4 [Controller]:** `MarketScanner` 리팩토링 (멀티스레딩 최적화 및 에러 핸들링 전담)
* **PBS-5 [Presentation]:** Streamlit 대시보드 (View 분리, 로직 완전 배제)

**[UML 모델링 계획]**
코드 구현 전, AI를 통해 다음 다이어그램을 마크다운(Mermaid.js)으로 추출하여 구조를 선행 검증합니다.

* **정적 모델링 (클래스 다이어그램):** Strategy 패턴이 적용된 분석 알고리즘의 상속 구조와, MVC 각 계층의 의존 관계를 시각화합니다.
* **동적 모델링 (시퀀스 다이어그램):** 사용자가 대시보드에서 스캔을 누른 후 -> Controller -> DataFetcher -> Strategy -> UI로 데이터가 흐르는 과정을 명세합니다.

### D. 모듈화 및 객체지향 설계 제약 (Modularity & OOP)

* **결합도와 응집도 제어:**
* **데이터 결합도(Data Coupling) 지향:** 모듈 간 데이터를 주고받을 때 튜플이나 전역 상태를 쓰지 않고, 명확하게 정의된 DTO(Data Transfer Object)나 표준화된 Pandas DataFrame만 매개변수로 전달합니다.
* **기능적 응집도(Functional Cohesion) 확보:** 기존 `MarketScanner`가 짊어지던 JSON 파싱, 에러 핸들링 책임을 각각 독립된 유틸리티 모듈로 분리하여 SRP(단일 책임 원칙)를 준수합니다.


* **SOLID 원칙 검증 지침:** * 비즈니스 로직은 외부 라이브러리(Streamlit 등)에 의존해서는 안 되며(DIP),
* 에러 발생 시 문자열(`"error"`) 반환이 아닌 사용자 정의 Exception 클래스를 던지도록 하여 예외 처리를 표준화합니다.



### E. UI/UX 제약 및 품질 보증(QA) 계획

* **UI/UX 원칙 (Streamlit 최적화):**
* **학습 용이성 & 멘탈 모델:** 사용자의 직관적인 조작을 위해 날짜나 타겟 시장 선택은 자유 텍스트가 아닌 제한된 콤보박스나 캘린더 위젯으로 강제합니다.
* **즉각적 피드백:** 멀티스레딩 스캔 중 멈춤 현상을 방지하기 위해 Streamlit의 `st.progress`와 `st.spinner`를 필수적으로 배치하여 시스템의 상태를 투명하게 제공합니다.
* **View 로직 분리:** 금액 단위를 "억", "원"으로 바꾸는 포맷팅 로직은 `app.py`에서 제거하고, Controller와 View 사이에 `ViewModel` 역할을 하는 포맷터(Formatter) 계층을 두어 처리합니다.


* **품질 측정 및 검증(QA):**
* **순환 복잡도(Cyclomatic Complexity) 제한:** 데이터 전처리 및 분석 함수의 제어 흐름 복잡도가 10을 초과하지 않도록 AI에게 강제하여, 함수당 길이를 극단적으로 줄입니다.
* **강인성(Robustness):** KIS API의 초당 호출 제한(Rate Limit)이나 네트워크 타임아웃 발생 시, 시스템이 종료되지 않고 실패한 종목만 로깅한 뒤 다음 스캔으로 넘어가도록 전역 예외 처리(Try-Except)를 구현합니다.



---

**💡 PM / 시니어 아키텍트 코멘트:**
이 계획서는 구현을 위한 구체적인 코드가 아닌, 'AI 바이브코딩을 완벽하게 통제하기 위한 전략적 나침반'입니다. 이 초안을 GitHub Issue에 업로드하여 SE 프로세스의 시작점으로 삼고, 이후 PBS-1부터 차례대로 AI에게 프롬프팅하여 개발을 진행하는 것을 권장합니다.