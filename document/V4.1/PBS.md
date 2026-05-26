수정된 **[Stock_Program_V4.1] 아키텍처 및 소프트웨어 공학 기반 추가 패치 계획서**를 완벽하게 반영하여, 바이브코딩에 즉시 투입할 수 있는 4단계의 **PBS (Prompt Breakdown Structure) 명세서**를 작성했습니다.

이번 패치의 핵심인 'V3 비즈니스 로직의 TDD 기반 복원'을 최우선 단계(`PBS-4.1.0`)로 배치하여 시스템의 신뢰성을 먼저 확보한 뒤, 구조 개선과 UI 분리를 진행하도록 설계했습니다.

아래 프롬프트 템플릿을 복사하여 순차적으로 실행해 주십시오.

---

# [Stock_Program_V4.1] PBS 프롬프트 명세서

## [PBS-4.1.0] 비즈니스 로직 복원 (V3 룰 이식)

* **Target:** `core/strategy.py`, `tests/test_strategy.py`
* **설명:** V4 리팩토링 과정에서 단순화되었던 P2(6단계 수급 필터) 및 P3 로직을 V3 수준의 정교함으로 복원합니다. AI-TDD를 적용하여 로직의 무결성을 검증합니다.

**[Prompt Template - 복사해서 사용하세요]**

```text
당신은 AI-TDD 방법론을 준수하는 시니어 퀀트 엔지니어입니다. V4 리팩토링 중 누락된 V3 레거시의 정교한 비즈니스 룰을 `core/strategy.py`에 복원하십시오.

[수정 지침]
1. AI-TDD 강제: 코드를 수정하기 전, `tests/test_strategy.py`를 먼저 업데이트하십시오. P2의 6단계 필터(가격, 150억/500억 유동성 조건, 이격도, 매수 트리거, 100억/30억 규모 조건) 각각의 실패/성공 케이스를 검증하는 단위 테스트를 작성해야 합니다.
2. `P2Strategy` 복원: V3의 `check_p2_supply_demand`에 있던 6단계 필터 로직을 이식하십시오. 결과 반환(Dictionary) 시, 단순 True/False뿐만 아니라 V3처럼 `p2_stage`("초기포착" 또는 추세확정")와 `p2_reason`("외인주도(3일)" 등) 키를 반드시 포함하십시오. 복잡도(Cyclomatic Complexity)를 낮추기 위해 조건 검증은 내부 private 헬퍼 메서드로 쪼개십시오.
3. `P3Strategy` 복원: V3의 `check_sniper_filter`처럼 반환 딕셔너리에 `reason: "Vol Surge +59.0%"` 형태의 텍스트가 포함되도록 수정하십시오.
4. 모든 전략 클래스는 외부 상태에 의존하지 않는 순수 함수(Pure Function) 형태를 엄격히 유지하십시오.

```

---

## [PBS-4.1.1] 기능 제거 및 응집도 향상 (섹터 로직 완전 제거)

* **Target:** `core/market_scanner.py`, `ui/app.py`, `ui/formatters.py`
* **설명:** 데이터 소스(`tickers.json`)에 존재하지 않는 무의미한 'UNKNOWN' 섹터 집계 로직을 시스템 전 계층에서 깨끗하게 도려냅니다.

**[Prompt Template - 복사해서 사용하세요]**

```text
당신은 시스템의 응집도를 높이는 시니어 백엔드 개발자입니다. 현재 데이터 소스에 존재하지 않는 허위 섹터 정보로 인해 무의미한 'UNKNOWN' 집계가 발생하고 있습니다. 다음 세 파일을 수정하여 섹터 관련 로직을 완벽히 제거하십시오.

[수정 지침]
1. `core/market_scanner.py`: `aggregate_top_sectors` 메서드를 완전히 삭제하고, `run_scan`의 반환 딕셔너리에서 `"sectors"` 키와 결과값을 제거하십시오.
2. `ui/formatters.py`: `format_sectors` 함수를 완전히 삭제하십시오.
3. `ui/app.py`: `render_results` 함수의 파라미터에서 `sectors`를 제거하십시오. 상단 요약 메트릭 중 "주도 섹터"를 삭제하고 2개의 컬럼(선별 종목, 분석 실패)으로 레이아웃을 조정하십시오. `st.subheader("주도 섹터")` 및 관련 테이블 렌더링 코드를 완전히 삭제하십시오.

```

---

## [PBS-4.1.2] 통합 스캔 파이프라인 (코스피+코스닥 동시 스캔)

* **Target:** `ui/app.py`, `core/utils.py` (또는 `tickers.json` 로드 로직 위치)
* **설명:** 사용자가 하나의 시장만 선택하던 구조를 다중 선택으로 바꾸고, 선택된 두 시장의 데이터를 파사드 패턴을 통해 하나의 DataFrame으로 병합하여 스레드 풀에 넘깁니다.

**[Prompt Template - 복사해서 사용하세요]**

```text
당신은 데이터 파이프라인을 설계하는 시니어 백엔드 개발자입니다. KOSPI와 KOSDAQ 시장을 각각 스캔하여 합치는 V3의 장점을 복원하되, V4의 효율적인 단일 멀티스레딩 파이프라인을 유지하도록 수정하십시오.

[수정 지침]
1. `ui/app.py` (멘탈 모델 변경): 사이드바의 `selectbox`를 `st.sidebar.multiselect`로 변경하십시오. 옵션은 `["KOSPI", "KOSDAQ"]`으로 하고 기본값으로 두 시장이 모두 선택되도록 설정하십시오. 스캔 대상이 늘어나므로 `st.progress`와 `st.spinner`의 상태 메시지 표시가 명확히 이루어지도록 유지하십시오.
2. `core/utils.py` (파사드 패턴): `load_tickers` 함수가 `market_type` 파라미터로 단일 문자열이 아닌 **리스트(List[str])**를 받도록 시그니처를 변경하십시오. 리스트를 순회하며 각각의 시장을 필터링한 뒤, `pd.concat`을 사용하여 하나의 DataFrame으로 병합(Merge)하여 반환하도록 캡슐화하십시오.

```

---

## [PBS-4.1.3] 다중 뷰(View) 렌더링 (P1/P2/P3 완벽 분리)

* **Target:** `ui/formatters.py`, `ui/app.py`
* **설명:** 한 덩어리로 렌더링되던 결과 표를 P1(지수 주도주), P2(수급 주도주), P3(급등 전조) 전용 포맷터와 UI 섹션으로 완벽하게 분리합니다.

**[Prompt Template - 복사해서 사용하세요]**

```text
당신은 MVC 아키텍처와 객체지향 설계(SRP)에 능숙한 프론트엔드 엔지니어입니다. 현재 `format_results` 하나로 뭉쳐져 있는 뷰를 P1, P2, P3 3개의 독립된 뷰로 분리하십시오.

[수정 지침]
1. `ui/formatters.py` (응집도 극대화): 기존 `format_results`를 삭제하고 `format_p1`, `format_p2`, `format_p3` 세 개의 순수 함수를 작성하십시오. 공통 포맷팅(금액, 퍼센트)은 헬퍼 함수를 재사용하십시오.
   - [P1 포맷터]: 종목코드, 종목명, 현재가, 등락률, 기여점수, 외국인순매수, 기관순매수 컬럼만 추출.
   - [P2 포맷터]: 종목코드, 종목명, 단계, 포착사유, 현재가, 등락률 컬럼 추출. (단계는 `p2_stage`, 포착사유는 `p2_reason` 활용).
   - [P3 포맷터]: 종목코드, 종목명, 현재가, 등락률, Vol Surge, 외국인순매수, 기관순매수 컬럼 추출. (Vol Surge는 P3 Strategy에서 반환된 텍스트 데이터 활용).
2. `ui/app.py` (DIP 준수): `render_results` 수정 시 비즈니스 판단 로직을 넣지 마십시오. 넘겨받은 `results` DataFrame을 `is_p1 == True`, `is_p2 == True`, `is_p3 == True` 플래그로만 필터링하여 3개의 데이터프레임으로 나누십시오. `st.tabs` 또는 3개의 `st.subheader`를 사용하여 "P1: 지수 주도주", "P2: 수급 주도주", "P3: 급등 전조" 섹션을 나누고 전용 포맷터를 거친 데이터를 각각 렌더링하십시오.

```