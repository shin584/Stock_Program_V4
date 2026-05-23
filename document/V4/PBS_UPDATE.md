# [PBS 0~5 프롬프트 명세서] (V4 리팩토링 업데이트판)

## **[➕추가/수정됨] PBS-0 [Configuration]: 전역 설정 로드 및 검증 모듈**

* **Target:** `core/config.py`
* **Input Files:** `legacy_code/config.py`

**[Prompt Template - 복사해서 사용하세요]**

```text
당신은 파이썬 시니어 백엔드 개발자입니다. 첨부된 레거시 `config.py`를 파기하고, Fail-Fast 원칙에 입각하여 완전히 새로운 `core/config.py`를 작성해 주십시오.

[설계 제약사항]
1. 경로 호환성 보장: `os.path.dirname`을 중첩하는 방식 대신, 객체지향적인 `pathlib.Path`를 사용하여 루트 디렉토리의 `secrets.json` 파일을 찾도록 설계하십시오.
2. 예외 처리 표준화: 모듈 상단에 사용자 정의 예외인 `ConfigError(Exception)`를 선언하십시오.
3. Fail-Fast 원칙 적용: `load_secrets()` 함수 내에서 파일을 읽었을 때 `APP_KEY`, `APP_SECRET`, `ACCOUNT_NO` 등 필수 키가 하나라도 누락되었거나 파일을 찾을 수 없는 경우, 조용히 `pass`하거나 빈 딕셔너리를 반환하지 말고 즉시 `raise ConfigError`를 발생시켜 시스템을 중단시키십시오.

```

---

## PBS-1 [Infrastructure]: KIS API 통신 모듈 및 토큰 관리

* **Target:** `api/kis_client.py`
* **Input Files:** `legacy_code/kis_client.py`, `UML_Model.md`, `Use_Case_Text.md`

**[Prompt Template - 복사해서 사용하세요]**

```text
당신은 시니어 파이썬 백엔드 개발자입니다. 첨부된 기존 레거시 `kis_client.py`의 API 호출 로직을 참고하되, 다음의 엄격한 UML 구조와 예외 처리 룰을 준수하여 완전히 새로운 `api/kis_client.py`를 작성해 주십시오.

[설계 제약사항]
1. 패턴 적용: UML 클래스 다이어그램에 명시된 대로 `KisClient` 클래스에 **싱글톤(Singleton) 패턴**을 완벽하게 적용하십시오. 정적 변수 `_instance`와 클래스 메서드 `get_instance()`를 구현하여 토큰의 전역적 단일 관리를 보장해야 합니다.
2. 필수 메서드: UML에 명시된 `fetch_market_data(ticker)`, `refresh_token()` 메서드를 반드시 포함하십시오.
3. 예외 흐름 처리: 유스케이스 명세서의 [3a. 토큰 만료 시] 토큰을 자동 갱신하고 재시도하는 로직과, [3b. Rate Limit 초과 시] 지수 백오프(Exponential Backoff)를 적용하여 대기 후 재요청하는 로직을 내부에 캡슐화하십시오.
4. 로직 분리: 이 클래스는 순수하게 API 통신과 JSON 응답만 반환하며, 데이터프레임 변환 등의 로직은 절대 포함하지 마십시오.

```

---

## PBS-2 [Data Layer]: 데이터 전처리 및 지표 계산 모듈

* **Target:** `core/data_fetcher.py`
* **Input Files:** `api/kis_client.py` (PBS-1 결과물), `legacy_code/indicators.py`, `UML_Model.md`, `Use_Case_Text.md`

**[Prompt Template - 복사해서 사용하세요]**

```text
당신은 데이터 엔지니어링에 능숙한 파이썬 시니어 개발자입니다. KIS API에서 받은 JSON 데이터를 Pandas DataFrame으로 가공하는 `core/data_fetcher.py`를 작성해 주십시오.

[설계 제약사항]
1. 클래스 구조: UML 다이어그램에 명시된 `DataFetcher` 클래스를 작성하십시오.
2. 메서드 구현: 내부적으로 KisClient.get_instance()를 호출하여 데이터를 받아오고, 정형화된 DataFrame을 반환하는 `get_and_process_data(ticker)`를 구현하십시오.
3. 데이터 결합도: 에러 발생 시 튜플(df, error)을 반환하지 말고, 오직 완성된 DataFrame 객체 하나만 반환하거나 Exception을 발생시키십시오.
4. [➕추가/수정됨] 모듈 통합 및 방어적 프로그래밍: 첨부된 레거시 `indicators.py`의 계산 로직(MA, MACD)을 `DataFetcher` 내부의 은닉된 순수 함수 `_calculate_indicators(df)`로 흡수 병합하여 응집도를 높이십시오. 지표 계산 전 `if df.empty or '종가' not in df.columns:` 와 같은 방어(검증) 로직을 반드시 추가하고, 실패 시 표준화된 `DataNotSufficientError` 예외를 발생시키십시오.

```

---

## PBS-3 [Business Logic]: 주도주 및 섹터 판별 알고리즘 (핵심)

* **Target:** `tests/test_strategy.py`, `core/strategy.py`
* **Input Files:** `Use_Case_Text.md` (비즈니스 룰 1~3 참조), `UML_Model.md`

**[Prompt Template - 복사해서 사용하세요]**

```text
당신은 AI-TDD(테스트 주도 개발) 방법론을 엄격하게 준수하는 시니어 퀀트 엔지니어입니다. 유스케이스의 [비즈니스 룰 1~3]을 검증하고 실행하는 로직을 작성합니다.

[설계 제약사항]
1. AI-TDD 강제 (가장 중요): `core/strategy.py`의 본문 코드를 작성하기 전에, **반드시 `pytest` 기반의 단위 테스트 코드(`tests/test_strategy.py`)를 먼저 작성하여 출력**하십시오. 테스트 코드에는 각 P1, P2, P3 룰에 부합하는 Mock DataFrame 데이터를 주입하여 True/False가 정확히 반환되는지 검증해야 합니다.
2. 전략 패턴 (Strategy Pattern): UML에 명시된 대로 `SectorAnalysisStrategy` 인터페이스 추상 클래스를 작성하고, 이를 상속받는 `P1Strategy`, `P2Strategy`, `P3Strategy` 클래스를 구현하십시오.
3. 순수 함수 강제: 각 전략 클래스의 `analyze(df)` 메서드는 외부 상태(API, DB, UI)에 절대 의존하지 않는 **순수 함수(Pure Function)**여야 합니다. 오직 DataFrame을 입력받아 분석 결과(Dict)만 반환하십시오.

```

---

## PBS-4 [Controller]: MarketScanner 리팩토링

* **Target:** `core/market_scanner.py`
* **Input Files:** `legacy_code/pipeline.py` (참조용), `core/data_fetcher.py`, `core/strategy.py`, `UML_Model.md`, `Use_Case_Text.md`

**[Prompt Template - 복사해서 사용하세요]**

```text
당신은 시스템의 제어 흐름을 설계하는 시니어 백엔드 개발자입니다. 레거시 `pipeline.py`를 파기하고 새로운 Controller 역할의 `core/market_scanner.py`를 작성해 주십시오.

[설계 제약사항]
1. [➕추가/수정됨] 의존성 주입 (DI) 및 SRP 준수: `MarketScanner` 클래스 내부에서 `DataFetcher()`를 묻지마 생성하지 말고(DIP 위배 방지), 생성자를 통해 인스턴스를 주입(Inject)받도록 설계하십시오. 또한, 기존 레거시에 있던 `tickers.json` 로드 로직은 컨트롤러의 책임 밖이므로 별도의 유틸리티 함수로 분리하십시오 (God Object 해소). 또한, 기존 레거시에 있던 tickers.json 로드 로직은 컨트롤러의 책임 밖이므로, core/utils.py라는 별도의 파일을 생성하여 해당 파일 내부에 유틸리티 함수로 분리하십시오.

2. [➕추가/수정됨] 예외 캐치 표준화: 기존의 튜플(`df, error`) 반환 안티 패턴을 완전히 폐기하십시오. `run_scan`의 멀티스레딩 워커 함수(`process_stock`) 내부에서 하위 모듈이 던지는 예외(`KisApiError`, `DataNotSufficientError` 등)를 철저히 `try-except`로 캐치하십시오. 실패한 종목은 `failures` 리스트에 격리한 뒤 다음 스캔을 중단 없이 계속 진행하는 강인한(Robust) 구조로 전면 개편해야 합니다.
3. 섹터 집계 로직: 유스케이스의 [Rule 4]를 반영하여, 스캔이 완료된 종목 데이터를 바탕으로 P1/P2 종목이 가장 많이 포함된 상위 3개 섹터를 도출해 내는 로직을 구현하십시오.

```

---

## PBS-5 [Presentation]: Streamlit 대시보드 UI

* **Target:** `ui/app.py`
* **Input Files:** `core/market_scanner.py`, `UML_Model.md`

**[Prompt Template - 복사해서 사용하세요]**

```text
당신은 UX/UI 원칙과 MVC 아키텍처에 능숙한 프론트엔드 엔지니어입니다. Streamlit을 사용하여 사용자에게 결과를 보여주는 `ui/app.py`를 작성해 주십시오.

[설계 제약사항]
1. View 로직 완전 분리: 이 파일에는 데이터를 계산하거나 판별하는 비즈니스 로직을 절대 포함하지 마십시오. 오직 `MarketScanner` 컨트롤러를 호출하고 그 결과값만 렌더링해야 합니다. 금액 단위를 변환('억', '원')하는 포맷팅 로직도 ViewModel/포맷터 계층으로 분리하여 순수 UI 코드만 남기십시오.
2. 필수 메서드: UML 다이어그램에 명시된 `StreamlitUI` 클래스 구조를 활용하여 `select_date()`, `click_scan()`, `render_results(results, sectors, failures)` 함수/메서드를 구현하십시오.
3. 즉각적 피드백: 스캔 중지 현상을 방지하고 사용자 경험을 높이기 위해 `st.progress`와 `st.spinner`를 활용한 진행 상태 표시를 반드시 구현하십시오.
4. 예외 UI 표시: 휴장일 에러나 분석 실패 종목 리스트를 보여주는 유스케이스 [3c, 3d] 시나리오의 UI 레이아웃을 반영하십시오.
5. 의존성 조립 (Composition Root): app.py는 애플리케이션의 진입점이므로, 실행 시 core/config.py의 SETTINGS를 바탕으로 KisClient, DataFetcher, 그리고 P1, P2, P3 Strategy 객체들을 초기화하고, 이를 MarketScanner 생성자에 주입(Inject)하여 시스템을 조립하는 로직을 상단에 포함하십시오.

```