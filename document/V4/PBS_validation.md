### PBS-0 준수 여부 체크리스트
1. 경로 호환성 보장 (Pathlib 사용) : ✅ 완벽함

요구사항: os.path.dirname을 중첩하는 대신 pathlib.Path를 사용할 것.

구현 확인: ROOT_DIR = Path(__file__).resolve().parents[1]를 사용하여 현재 파일 위치를 기준으로 두 단계 상위(루트) 폴더를 정확하고 객체지향적으로 찾아냈습니다. (운영체제 상관없이 완벽히 동작합니다)

2. 예외 처리 표준화 (사용자 정의 예외) : ✅ 완벽함

요구사항: 모듈 상단에 ConfigError(Exception)를 선언할 것.

구현 확인: 파일 최상단에 ConfigError 클래스를 선언하여, 향후 설정 관련 에러가 터졌을 때 디버깅이 매우 쉽도록 계층을 잘 분리했습니다.

3. Fail-Fast 원칙 적용 (필수 키 검증) : ✅ 완벽함

요구사항: 파일이 없거나 APP_KEY, APP_SECRET, ACCOUNT_NO 중 하나라도 누락되면 조용히 넘기지 말고 즉시 raise ConfigError를 발생시킬 것.

구현 확인:

파일 존재 여부 검사 (if not secrets_path.exists(): raise ConfigError...)

JSON 포맷 불량 및 읽기 에러 검사 (try-except 구조로 명시적 예외 발생)

필수 키 누락 검사: REQUIRED_SECRET_KEYS를 순회하며 키가 아예 없거나 값이 비어있는 경우(strip() 활용)를 모두 잡아내어 에러를 던지도록 완벽하게 방어했습니다.

### PBS-1 준수 여부 체크리스트
1. 패턴 적용 (싱글톤 패턴) : ✅ 완벽함

요구사항: _instance 정적 변수와 get_instance() 클래스 메서드를 통해 전역적 단일 관리를 보장해야 함.

구현 확인: * _instance: Optional["KisClient"] = None 선언과 @classmethod get_instance 팩토리 메서드가 정확히 구현되었습니다.

특히 __init__ 내부에 if getattr(self, "_initialized", False): return 방어 로직을 넣어, 인스턴스화가 여러 번 시도되더라도 토큰 변수가 중복 초기화되는 것을 막아낸 점이 훌륭합니다.

2. 필수 메서드 구현 : ✅ 완벽함

요구사항: fetch_market_data(ticker), refresh_token() 메서드 포함.

구현 확인: 두 메서드 모두 명확한 타입 힌트(-> Dict[str, Any], -> None)와 함께 정확한 이름으로 구현되었습니다.

3. 예외 흐름 처리 (3a, 3b) : ✅ 완벽함

요구사항: [3a] 토큰 만료 시 자동 갱신 및 재시도, [3b] Rate Limit 초과 시 지수 백오프 적용 후 재시도.

구현 확인: _send_request 캡슐화 메서드 내부에서 완벽하게 처리되었습니다.

[3a] 토큰 만료: HTTP 상태 코드가 401이거나 응답 페이로드가 인증 에러(_is_auth_error_payload)인 경우, 즉시 self.refresh_token()을 호출하고 continue를 통해 기존 요청을 재시도합니다.

[3b] Rate Limit 초과: _is_rate_limited 조건에 걸리면 wait_time = 0.5 * (2  attempt)를 계산하여 점진적으로 대기 시간을 늘리는 지수 백오프(Exponential Backoff)가 정확히 적용되었습니다.

4. 로직 분리 (데이터프레임 변환 금지) : ✅ 완벽함

요구사항: 순수하게 API 통신과 JSON 응답만 반환하고, DataFrame 변환 로직 배제.

구현 확인: 파일 상단의 import 문을 보면 pandas가 전혀 포함되어 있지 않습니다. KIS API 통신 결과는 철저히 파이썬 딕셔너리(Dict[str, Any]) 형태로만 반환하여 단일 책임 원칙(SRP)을 훌륭하게 지켜냈습니다.

제공해주신 `data_fetcher.py` 코드를 업데이트된 **[PBS-2] 명세서**의 제약사항을 기준으로 면밀히 검토했습니다.

결론부터 말씀드리면, **[PBS-2]의 모든 설계 제약사항을 완벽하게 준수했으며, 방어적 프로그래밍 측면에서 매우 뛰어난 품질(A+)을 보여주는 코드입니다.** 특히 JSON 파싱(`_extract_records`)과 병합 과정에서의 디테일이 인상적입니다.

아래는 PBS-2의 4가지 제약사항에 대한 구체적인 검토 결과입니다.

---

### PBS-2 준수 여부 체크리스트

**1. 클래스 구조 (`DataFetcher`) : ✅ 완벽함**

* **요구사항:** UML에 명시된 `DataFetcher` 클래스를 작성할 것.
* **구현 확인:** 명시된 대로 `DataFetcher` 클래스가 잘 구현되어 있습니다.

**2. 메서드 구현 (`get_and_process_data`) : ✅ 완벽함**

* **요구사항:** 내부적으로 `KisClient`를 호출하여 데이터를 받고, 완성된 DataFrame을 반환할 것.
* **구현 확인:** `get_and_process_data` 메서드에서 `KisClient.get_instance()`를 통해 데이터를 받아온 뒤, 가격 데이터와 매매동향 데이터를 각각 만들고 병합(`_merge_frames`)한 후 지표를 계산(`_calculate_indicators`)하여 하나의 DataFrame으로 반환하는 흐름이 매우 깔끔하게 구현되었습니다.

**3. 데이터 결합도 (튜플 반환 금지) : ✅ 완벽함**

* **요구사항:** 에러 발생 시 `(df, error)` 튜플을 반환하지 말고, 오직 완성된 DataFrame 하나만 반환하거나 Exception을 발생시킬 것.
* **구현 확인:** 튜플 반환 안티 패턴이 완전히 제거되었습니다. 반환 타입이 `-> pd.DataFrame`으로 명확하며, 데이터가 비어있거나 올바르지 않으면 즉각적으로 `DataNotSufficientError`를 `raise`하여 Fail-Fast 원칙을 완벽히 준수했습니다.

**4. 모듈 통합 및 방어적 프로그래밍 (`indicators.py` 흡수) : ✅ 완벽함**

* **요구사항:** 레거시 `indicators.py` 로직을 `_calculate_indicators(df)` 순수 함수로 흡수 병합하고, 계산 전 DataFrame 검증 방어 로직을 추가할 것.
* **구현 확인:** * 기존 로직이 `_calculate_indicators`라는 클래스 내부의 Private 메서드로 완벽히 흡수되었습니다.
* 메서드 최상단에 `if df.empty or "종가" not in df.columns:` 방어 로직이 정확히 위치하며, 조건을 통과하지 못하면 명시적으로 `DataNotSufficientError`를 발생시킵니다.
* 심지어 문자열이 섞여 있을 경우를 대비해 `pd.to_numeric`으로 강제 형변환까지 수행하는 점은 백엔드 개발자로서 훌륭한 디테일입니다.



---

### PM의 마이크로 피드백 (단 한 가지 아쉬운 점)

코드는 완벽하게 동작하지만, **의존성 역전 원칙(DIP)** 관점에서 생성자(`__init__`) 부분이 살짝 아쉽습니다.

**현재 코드:**

```python
    def __init__(self) -> None:
        config = get_kis_config()
        self.kis_client = KisClient.get_instance(**config)

```

* **이유:** 이렇게 작성하면 `DataFetcher`가 `KisClient` 객체를 스스로 찾아와서 생성하게 됩니다. 나중에 테스트를 할 때 가짜 통신 모듈(Mock)을 끼워 넣기가 조금 번거로워집니다.

**더 완벽한 코드 (수정 권장):**

```python
    def __init__(self, kis_client: Optional[KisClient] = None) -> None:
        """
        [Why] 의존성 주입(DI): KisClient를 외부에서 주입받아 테스트(Mocking)를 용이하게 합니다.
        """
        if kis_client:
            self.kis_client = kis_client
        else:
            config = get_kis_config()
            self.kis_client = KisClient.get_instance(**config)

```

이렇게 외부에서 `kis_client`를 주입(Inject)받을 수 있는 통로를 하나 열어두면, 객체 지향의 유연성이 극대화됩니다.

 - 테스트 코드

```powershell
python -m py_compile Stock_Program_V4\core\data_fetcher.py
```

그리고 샘플 KIS JSON으로 전처리/지표 계산을 확인한 코드는 아래입니다.

```powershell
python -c "from Stock_Program_V4.core.data_fetcher import DataFetcher; f=object.__new__(DataFetcher); raw={'price': {'output2': [{'stck_bsop_date':'20250101','stck_clpr':'100','acml_vol':'10','acml_tr_pbmn':'1000'}, {'stck_bsop_date':'20250102','stck_clpr':'110','acml_vol':'20','acml_tr_pbmn':'2200'}, {'stck_bsop_date':'20250103','stck_clpr':'121','acml_vol':'30','acml_tr_pbmn':'3630'}, {'stck_bsop_date':'20250104','stck_clpr':'120','acml_vol':'40','acml_tr_pbmn':'4800'}, {'stck_bsop_date':'20250105','stck_clpr':'130','acml_vol':'50','acml_tr_pbmn':'6500'}]}, 'investor': {'output': [{'stck_bsop_date':'20250105','frgn_ntby_tr_pbmn':'300','orgn_ntby_tr_pbmn':'200'}]}}; df=f._calculate_indicators(f._merge_frames(f._build_price_frame(raw['price']), f._build_investor_frame(raw['investor']))); print(list(df.columns)); print(len(df), round(float(df.iloc[-1]['MACD']), 4))"
```

출력은 다음과 같았습니다.

```text
['종가', '거래량', '거래대금', '등락률', '외국인_순매수금액', '기관_순매수금액', 'MA5', 'MA20', 'MA60', 'MACD', 'Signal', 'MACD_Oscillator']
5 4.9485
```

추가 패치 반영 확인 사항
생성자(__init__)의 의존성 주입 (DIP 준수)

kis_client: Optional[KisClient] = None을 통해 외부에서 KisClient 인스턴스를 주입받을 수 있도록 변경되었습니다.

if kis_client is not None: 조건을 통해, 주입된 인스턴스가 있으면 그것을 사용하고, 없을 때만 get_kis_config()와 KisClient.get_instance()를 호출하도록 방어적으로 구현되었습니다.

### PBS-3 준수 여부 체크리스트
1. AI-TDD 강제 (테스트 코드 선행) : ✅ 완벽함

요구사항: test_strategy.py를 작성하여 Mock DataFrame 데이터를 주입하고 True/False를 검증할 것.

구현 확인: * test_strategy.py 파일이 완벽하게 작성되었습니다.

_base_frame(rows=20)이라는 픽스처(Fixture) 헬퍼 함수를 만들어 Mock DataFrame을 깔끔하게 생성하고 주입한 점이 돋보입니다.

P1, P2, P3 각각에 대해 통과(True)하는 케이스와 실패(False)하는 케이스를 명확한 assert 문으로 검증하여 신뢰성을 확보했습니다.

2. 전략 패턴 (Strategy Pattern) 적용 : ✅ 완벽함

요구사항: SectorAnalysisStrategy 추상 클래스를 작성하고 P1Strategy, P2Strategy, P3Strategy가 이를 상속받아 구현할 것.

구현 확인:

파이썬의 abc.ABC와 @abstractmethod를 사용하여 SectorAnalysisStrategy 인터페이스를 완벽하게 정의했습니다.

3개의 전략 클래스가 모두 이를 상속받아 개방-폐쇄 원칙(OCP)을 준수합니다. 향후 P4 전략이 추가되더라도 기존 코드를 전혀 수정할 필요가 없습니다.

3. 순수 함수 강제 (Pure Function) : ✅ 완벽함

요구사항: analyze(df) 메서드는 외부 상태(API, DB, UI)에 의존하지 않고 오직 DataFrame만 받아 분석 결과(Dict)를 반환할 것.

구현 확인:

메서드 내부에 API 호출이나 외부 상태 참조가 전혀 없습니다. 입력받은 df만을 사용하여 계산을 수행합니다.

_to_float, _count_consecutive_positive, _numeric_sum 등의 은닉된(Private) 유틸리티 함수를 밖으로 빼내어 analyze 내부의 복잡도를 낮추고 응집도를 높인 점은 시니어급 설계입니다.

반환값 역시 {"strategy": "P2", "is_p2": True, ...} 형태의 순수 Dictionary로 고정하여 데이터 결합도를 완벽히 통제했습니다.

### PBS-4 준수 여부 체크리스트
1. 의존성 주입 (DI) 및 SRP 준수 : ✅ 완벽함

요구사항: MarketScanner 내부에서 DataFetcher() 등을 직접 생성(God Object 패턴)하지 말고, 생성자에서 주입받을 것. tickers.json 로드 로직은 유틸리티로 뺄 것.

구현 확인:

__init__ 메서드를 보면 data_fetcher: DataFetcher와 strategies: Sequence[SectorAnalysisStrategy]를 파라미터로 명확하게 주입(Inject)받고 있습니다. 내부에서 불필요한 객체 생성이 원천 차단되었습니다.

종목 로드(파일 IO) 로직이 컨트롤러에서 완전히 삭제되었으며, run_scan 메서드는 외부에서 읽어온 데이터(tickers)만 파라미터로 받아 처리하도록 분리(SRP 준수)되었습니다.

2. 예외 캐치 표준화 및 강인성(Robustness) : ✅ 완벽함

요구사항: 튜플 반환 안티 패턴을 폐기하고, 워커 스레드(process_stock) 내부에서 하위 모듈의 예외(KisApiError, DataNotSufficientError)를 try-except로 캐치하여 스캔 중단 없이 failures 리스트로 격리할 것.

구현 확인:

_process_stock 내부가 견고한 try-except 블록으로 보호되어 있습니다.

에러가 발생해도 시스템이 죽지 않고, { "ok": False, "failure": {...} } 형태의 명확한 상태 객체를 반환합니다.

부모 스레드(run_scan)에서는 이를 받아 failures 리스트에 안전하게 쌓고 바로 다음 종목으로 넘어갑니다(continue). 완벽한 스레드 안전성(Thread Safety)을 확보했습니다.

3. 섹터 집계 로직 (Rule 4 반영) : ✅ 완벽함

요구사항: 스캔 결과를 바탕으로 P1/P2 종목이 가장 많은 상위 3개 섹터를 추출하는 aggregate_top_sectors() 메서드 구현.

구현 확인:

Pandas의 groupby, size, sort_values를 아주 우아하게 체이닝하여, P1이나 P2에 해당하는 종목(leaders = results_df[p1 | p2])을 섹터별로 정확하게 집계하고 상위 3개를 추출해냅니다.

### PBS-5 준수 여부 체크리스트
1. View 로직 완전 분리 (ViewModel 패턴 적용) : ✅ 완벽함

요구사항: 비즈니스 로직 배제, 금액 단위 변환('억', '원') 로직을 포맷터 계층으로 분리할 것.

구현 확인: app.py 내부에는 단 한 줄의 계산식도 없습니다. 모든 데이터 가공과 포맷팅은 새롭게 분리된 formatters.py에서 담당하며, UI는 오직 format_results가 예쁘게 포장해 준 결과물만 화면에 그립니다. 교과서적인 MVC/MVVM 패턴의 적용입니다.

2. 필수 메서드 구현 (StreamlitUI 클래스) : ✅ 완벽함

요구사항: StreamlitUI 클래스 구조를 활용하여 select_date(), click_scan(), render_results() 구현.

구현 확인: 명시된 클래스와 세 가지 메서드가 정확히 구현되어 있으며, 컴포넌트 단위로 UI가 잘 모듈화되었습니다.

3. 즉각적 피드백 (st.progress, st.spinner) : ✅ 완벽함

요구사항: 멀티스레딩 스캔 중 시스템 상태를 사용자에게 투명하게 보여줄 것.

구현 확인: st.spinner로 전체 스캔 상태를 감싸고, update_progress라는 콜백 함수를 만들어 MarketScanner에 넘겨주었습니다. 스레드가 하나씩 끝날 때마다 프로그레스 바가 실시간으로 차오르기 때문에 사용자가 답답함을 느끼지 않습니다.

4. 예외 UI 표시 (강인성 시각화) : ✅ 완벽함

요구사항: 분석 실패 종목 리스트(데이터 부족, 에러 등)를 보여줄 것.

구현 확인: 에러 발생 시 프로그램이 멈추는 대신, failures 리스트를 모아 화면 하단 st.expander("실패 상세 보기") 영역에 깔끔하게 표출합니다.

5. 의존성 조립 (Composition Root) - 💡 핵심 포인트 : ✅ 완벽함

요구사항: 애플리케이션 진입점으로서 모든 모듈을 생성하고 MarketScanner에 주입(DI)할 것.

구현 확인: @st.cache_resource가 적용된 build_scanner() 함수가 그 역할을 완벽히 수행합니다!

get_kis_config()로 설정을 불러오고,

KisClient 싱글톤을 초기화한 뒤,

DataFetcher에 주입하고,

3가지 전략과 함께 최종적으로 MarketScanner를 조립해 냅니다.
Streamlit의 캐싱 기능을 활용하여 매번 새로 객체를 만들지 않도록 최적화한 점은 시니어급 프론트엔드 스킬입니다.