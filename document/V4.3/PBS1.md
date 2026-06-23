

### 📦 [Step 1] 도메인 객체 설계 및 불변성 강제 (Domain & Value Object)

가장 먼저 `pykrx`에서 받아올 단순 문자열 리스트(원시 타입)를 대체할, '읽기 전용' 특수 객체를 만듭니다.

**📋 복사/붙여넣기용 프롬프트:**

```text
당신은 엄격한 객체지향 원칙을 준수하는 시니어 파이썬 백엔드 개발자입니다. 
주식 분석 시스템의 '타겟 유니버스(코스피 200, 코스닥 150 종목 코드 집합)'를 관리하기 위한 Value Object 클래스인 `MarketUniverse`를 구현해야 합니다.

[설계 제약 사항]
1. 원시 타입 지양 (Primitive Obsession 방지): 단순히 list나 set을 사용하지 말고, 내부적으로 코스피 200 목록과 코스닥 150 목록을 각각 set 자료형으로 가지는 `MarketUniverse` 클래스를 작성하세요.
2. 불변성 (Immutability): 이 객체는 생성 시점(`__init__`)에 종목 리스트를 주입받은 이후, 외부에서 절대 데이터를 수정, 추가, 삭제할 수 없어야 합니다. (@property 데코레이터 등을 활용하여 캡슐화하고 숨은 가변성을 차단하세요.)
3. 편의 메서드: 두 시장의 종목 코드를 합친 전체 유니버스 셋을 반환하는 메서드(`get_all_tickers`)와, 특정 종목 코드가 유니버스에 포함되어 있는지 검증하는 메서드(`contains(ticker)`)를 포함하세요.

[AI-TDD 지시]
본격적인 클래스 코드를 작성하기 전에, 먼저 `pytest`를 사용한 테스트 코드(`test_market_universe.py`)를 작성하세요.
- 테스트 내용: 객체 생성 확인, `contains` 정상 동작 여부, 외부에서 강제로 내부 set을 수정하려고 할 때 예외가 발생하는지(불변성) 확인.
테스트 코드를 먼저 출력하고, 이어서 실제 `MarketUniverse` 클래스 코드를 작성해 주세요.

```

---

### 🔌 [Step 2] 외부 API 퍼사드 패턴 적용 (Facade Pattern)

Step 1에서 만든 안전한 `MarketUniverse` 객체에 실제 `pykrx` 데이터를 채워 넣는 창구를 만듭니다. 기존 프로그램이 `pykrx`에 직접 의존하지 않도록 격리합니다.

**📋 복사/붙여넣기용 프롬프트:**

```text
이전 단계에서 작성한 `MarketUniverse` 클래스를 활용하여, 외부 라이브러리인 `pykrx`와의 통신을 전담하는 `MarketDataFacade` 클래스를 구현합니다.

[컨텍스트: pykrx 명세]
- 코스피 200 지수 구성 종목 추출: `stock.get_index_portfolio_deposit_file("1028")`
- 코스닥 150 지수 구성 종목 추출: `stock.get_index_portfolio_deposit_file("2046")`

[설계 제약 사항]
1. 퍼사드 패턴 적용: 메인 비즈니스 로직에서는 `pykrx`를 직접 임포트하지 않아야 합니다. `MarketDataFacade` 클래스 내부에 `fetch_latest_universe()`라는 메서드를 만들고, 이 메서드가 pykrx를 호출하여 최신 종목 코드를 가져온 뒤, 앞서 만든 `MarketUniverse` 객체를 반환하도록 설계하세요.
2. 예외 처리: 네트워크 에러나 pykrx 내부 오류로 인해 데이터를 가져오지 못했을 경우에 대한 명확한 예외 처리(Try-Except)를 포함하세요.

[AI-TDD 지시]
구현 전 `pytest`와 `unittest.mock`을 활용한 테스트 코드(`test_market_data_facade.py`)를 먼저 작성하세요.
- 테스트 내용: pykrx의 `get_index_portfolio_deposit_file` 메서드를 Mocking하여 가짜 데이터를 반환하도록 설정한 뒤, `fetch_latest_universe()`가 올바른 `MarketUniverse` 객체를 생성하여 반환하는지 검증하세요.
테스트 코드를 먼저 출력하고, 이어서 실제 `MarketDataFacade` 코드를 작성해 주세요.

```

---

### ⏱️ [Step 3] 상태 관리 및 캐싱 (State Management & Caching)

장 마감 후 단 한 번만 업데이트되도록 호출 횟수를 통제하고, 리소스 낭비를 막는 단계입니다.

**📋 복사/붙여넣기용 프롬프트:**

```text
이전 단계에서 만든 `MarketDataFacade`를 활용하되, 프로그램 구동 중 불필요한 API 중복 호출을 막기 위한 '캐싱 및 수명 주기 제어' 계층을 구현합니다.

[설계 제약 사항]
1. 싱글톤(Singleton) 또는 캐싱: `UniverseStateManager`라는 클래스 (또는 모듈 레벨의 함수)를 만듭니다. 이 클래스는 `get_universe()` 호출 시, 메모리에 이미 로드된 `MarketUniverse` 객체가 있다면 그것을 즉시 반환하고, 없다면 `MarketDataFacade`를 통해 새로 생성하여 메모리에 저장(캐싱)한 뒤 반환해야 합니다.
2. 갱신 로직: 장 마감 후 매일 1회 최신화가 필요하므로, 캐시를 강제로 비우고 새로고침하는 `refresh_universe()` 메서드를 추가하세요.

[AI-TDD 지시]
구현 전 테스트 코드(`test_universe_state_manager.py`)를 먼저 작성하세요.
- 테스트 내용: `get_universe()`를 연속으로 3번 호출했을 때, 실제 `MarketDataFacade.fetch_latest_universe()`는 단 1번만 호출되는지(Mock의 call_count 확인) 검증하세요. 또한 `refresh_universe()` 호출 후 다시 `get_universe()`를 불렀을 때 새롭게 API가 호출되는지 확인하세요.
테스트 코드를 먼저 출력하고, 이어서 실제 상태 관리자 코드를 작성해 주세요.

```

---

### 🔄 [Step 4] 기존 시스템 호환 및 파이프라인 연동 (Legacy Adapter)

앞서 만든 `UniverseStateManager`를 이용해 가져온 종목 코드 목록을 기반으로, 기존 `tickers.json`이 제공하던 형태(코드, 이름, 시장, 시가총액)의 데이터를 생성하여 기존 시스템에 끊김 없이 공급하는 어댑터(함수)를 구현합니다.

**📋 복사/붙여넣기용 프롬프트:**

```text
지금까지 만든 `UniverseStateManager`와 pykrx를 활용하여, 기존 `core/utils.py`에 있던 `load_tickers` 함수를 완전히 대체하도록 리팩토링하세요. (더 이상 `tickers.json`을 읽지 않습니다.)

[설계 제약 사항]
1. 하위 호환성 유지 (Backward Compatibility): 리팩토링된 `load_tickers(top_n: int = 100)` 함수는 기존과 완벽하게 동일한 형태의 Pandas DataFrame (컬럼: `code`, `name`, `market`, `cap`)을 반환해야 합니다. 기존 `market_scanner.py` 등의 메인 비즈니스 로직을 전혀 수정하지 않기 위함입니다.
2. 부가 정보 매핑: `UniverseStateManager`를 통해 가져온 KOSPI 200 / KOSDAQ 150 티커 목록을 기반으로, pykrx의 조회 API(`stock.get_market_cap` 등)를 활용하여 시가총액과 종목명, 시장 구분(KOSPI/KOSDAQ)을 채워 넣으세요.
3. 정렬 및 필터링: KOSPI와 KOSDAQ 각각에 대해 (또는 통합하여) 시가총액(cap) 내림차순으로 정렬한 뒤, 사용자가 요청한 `top_n`개만큼 슬라이싱하여 최종 DataFrame으로 병합해 반환하세요.

[AI-TDD 지시]
리팩토링할 코드 작성 전에 해당 어댑터 로직을 검증할 수 있는 테스트 코드(`test_load_tickers_adapter.py`)를 먼저 작성하세요.
- 테스트 내용: mocker를 활용하여 `UniverseStateManager.get_universe()` 결과와 `pykrx` 시가총액 조회 반환값을 가짜로(Mock) 주입합니다. 이후 `load_tickers(top_n=2)`를 호출했을 때 예상되는 DataFrame 컬럼(code, name, market, cap)이 모두 존재하는지, 그리고 cap 기준 내림차순 정렬이 보장되는지 검증하세요.
테스트 코드를 먼저 출력하고, 이어서 실제 `core/utils.py` 리팩토링 코드를 작성해 주세요.
```
