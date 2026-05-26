

### [Stock_Program_Hotfix_V4.2] PBS 프롬프트 세트

#### [PBS-4.2.1] 데이터 무결성 복구 (Controller)

* **Target:** `core/market_scanner.py`
* **설명:** 조용히 버려지던(Silent Drop) 조건 미달 종목 25개를 명시적으로 추적하여 전체 200개 종목의 행방을 투명하게 관리합니다.

**[복사해서 사용하세요]**

```text
당신은 시스템의 무결성을 책임지는 백엔드 개발자입니다. 현재 `market_scanner.py`에서 P1, P2, P3 조건을 모두 통과하지 못한 종목이 아무 기록 없이 유실(Silent Drop)되는 문제가 있습니다. 200개의 스캔 대상이 100% 추적되도록 다음 지침에 따라 수정하십시오.

[수정 지침]
1. `_process_stock` 메서드 수정:
   - 종목이 전략 조건에 맞지 않을 때 (`not (result.get("is_p1") or ...)`), 기존처럼 `{"ok": True, "result": None}`을 반환하여 조용히 넘기지 마십시오.
   - 대신, `return {"ok": False, "failure": self._build_failure(ticker, name, "ConditionNotMet", "전략 조건 미달 (P1/P2/P3 모두 불합격)")}` 형태로 '조건 미달'임을 명시한 failure 데이터를 반환하도록 수정하십시오.
2. 검증: 이를 통해 `run_scan`이 종료되었을 때 `len(results) + len(failures)`가 항상 입력된 `tickers`의 수와 일치하도록 보장하십시오.

```


#### [PBS-4.2.2] P2 비즈니스 로직 모순 교정 (Model)

* **Target:** `core/strategy.py`
* **설명:** P2 전략 내부의 5일선 과열 기준과 20일선 단계 판별 기준이 충돌하여 무조건 "초기포착"만 출력되는 논리적 오류를 분리하여 해결합니다.

**[복사해서 사용하세요]**

```text
당신은 비즈니스 로직을 정교하게 다루는 퀀트 엔지니어입니다. 현재 `strategy.py`의 `P2Strategy`에 심각한 논리적 모순이 있습니다. 5일선 이격도(`disparity`)가 5.0 이하인 종목만 살려둔 뒤, 하단에서 `disparity <= 10.0`이면 "초기포착"을 부여하므로 항상 100% "초기포착"만 반환됩니다. 이를 해결하십시오.

[수정 지침]
1. 헬퍼 메서드 추가: 5일선 이격도와 별개로, **20일선 이격도**를 계산하여 반환하는 `_calculate_ma20_disparity(df)` 헬퍼 메서드를 새로 작성하십시오.
2. `P2Strategy.analyze` 수정: 
   - 기존의 `_calculate_ma5_disparity`는 상단의 '과열 탈락(5% 초과)' 필터용으로만 유지하십시오.
   - 하단의 `stage_text` 산출 로직 직전에 `_calculate_ma20_disparity`를 호출하십시오.
   - 20일선 이격도 값이 특정 임계값(예: 5.0% 또는 V3 기준 105%) 이하이면 "초기포착", 초과하면 "추세확정"으로 판별하도록 변수를 명확히 분리하여 캡슐화하십시오.

```

---

#### [PBS-4.2.3] P1 프레젠테이션 필터 적용 (View)

* **Target:** `ui/formatters.py`
* **설명:** Model 계층을 수정하지 않고, 순수하게 화면에 보여주기 직전(View)에 Top 5 종목만 잘라내어 결합도를 낮춥니다.

**[복사해서 사용하세요]**

```text
당신은 단일 책임 원칙(SRP)을 준수하는 프론트엔드 개발자입니다. `ui/formatters.py`의 `format_p1` 함수를 수정하여, 전체 P1 종목 중 상위 5개만 화면에 표출되도록 뷰 필터(View Filter)를 적용하십시오.

[수정 지침]
1. `format_p1` 내부 로직 수정: 인자로 넘어온 `results` DataFrame을 "기여점수" 기준으로 내림차순 정렬(`sort_values`)하십시오.
2. 정렬된 DataFrame에 `.head(5)`를 적용하여 최상위 5개 종목만 슬라이싱한 뒤 기존 포맷팅 로직으로 넘기십시오.
3. 이 수정은 전략 데이터 원본을 훼손하지 않고 오직 화면 표시 단계에만 영향을 주어야 합니다.

```

---

#### [PBS-4.2.4] 인지 모델 최적화 및 UI 재배치 (Controller/UI)

* **Target:** `ui/app.py`
* **설명:** 사용자의 시선 흐름에 맞게 '스캔 시작' 버튼을 메인 화면 중앙으로 옮기고, 추가된 '조건 미달' 데이터를 요약 지표에 반영합니다.

**[복사해서 사용하세요]**

```text
당신은 사용자 경험(UX) 최적화에 능숙한 UI/UX 엔지니어입니다. `ui/app.py`를 수정하여 멘탈 모델에 맞게 컴포넌트를 재배치하십시오.

[수정 지침]
1. `StreamlitUI` 클래스 수정:
   - `click_scan` 메서드를 완전히 삭제하십시오. (사이드바 버튼 제거)
   - `render_results`의 상단 메트릭(`st.columns`)을 3개로 확장하십시오. "선별 종목", "조건 미달(Skipped)", "API/에러 실패"로 나누어 표시하십시오. (Failure 리스트 내에서 `error_type == "ConditionNotMet"`인 것을 "조건 미달"로 분류).
2. `main()` 함수 흐름 수정:
   - `st.sidebar`에는 '스캔 종목 수', '동시 처리 수', '분석 기준일' 같은 환경 설정 옵션만 남기십시오.
   - 메인 컨테이너 영역(타이틀과 caption 바로 아래)에 매우 눈에 띄는 `st.button("전체 시장 스캔 시작", type="primary", use_container_width=True)`을 직접 배치하십시오.
   - 버튼이 눌렸을 때만 이후의 스캔 로직(`load_tickers`, `scanner.run_scan` 등)이 실행되도록 제어 흐름을 조정하십시오.

```

---
#### [PBS-4.2.5] 분석 기준일 시계열 파이프라인 동적 연결
Target: ui/app.py, core/market_scanner.py, core/data_fetcher.py, api/kis_client.py

설명: UI에서 선택한 과거의 특정 날짜가 API 엔드포인트의 조회 종료일(end_date)까지 안전하고 명시적으로 전달되도록 전체 데이터 라우팅 체인을 수정합니다.

[Prompt Template - 복사해서 사용하세요]
당신은 계층 간 결합도를 정교하게 제어하는 소프트웨어 아키텍트입니다. 현재 UI에서 선택한 '분석 기준일'이 최하단 KIS API 호출부까지 전달되지 않고 오늘 날짜로 고정되는 결함이 있습니다. 전역 변수를 배제하고 명시적 매개변수 주입 방식을 사용하여 데이터 파이프라인을 동적으로 연결하십시오.

[수정 지침]
1. api/kis_client.py 수정:
   - `fetch_market_data(self, ticker: str)` 메서드가 선택적 파라미터인 `target_date: Optional[datetime.date] = None`를 받도록 확장하십시오.
   - 메서드 내부에서 `end_date`를 계산할 때, `target_date`가 주어지면 `now()` 대신 해당 날짜의 자정(datetime 구성)을 기준점으로 삼고, `start_date`는 그 기준점으로부터 100일 전으로 계산하도록 하드코딩을 제거하십시오.

2. core/data_fetcher.py 및 core/market_scanner.py 수정:
   - `DataFetcher.get_and_process_data`, `MarketScanner.run_scan`, `MarketScanner._process_stock` 메서드 시그니처 전체에 `target_date: Optional[datetime.date] = None` 파라미터를 추가하십시오.
   - 상위 계층에서 하위 계층의 메서드를 호출할 때 이 `target_date`를 유기적으로 누락 없이 다운스트림 토싱(Passing)하도록 제어 흐름을 연결하십시오.

3. ui/app.py 수정:
   - `main()` 함수 내부에서 `scanner.run_scan`을 호출하는 시점에, 메인 화면 영역에서 캡처한 `selected_date` 객체를 `target_date=selected_date` 인자로 명시적으로 바인딩하여 호출하도록 수정하십시오.