

### 1. 동적 모델링: 시퀀스 다이어그램 (Sequence Diagram)

사용자가 메인 화면에서 '스캔 시작' 버튼을 누른 시점부터 4가지 이슈가 해결되어 화면에 렌더링되기까지의 데이터 제어 흐름(Control Flow)을 보여줍니다.

* **설계 포인트:** * `MarketScanner`에서 정상 데이터와 실패 데이터를 모두 수집하여 200개 유실 방지(무결성)를 보장합니다.
* P1 종목의 **Top 5 필터링**은 비즈니스 로직(Model)이 아닌 포맷터(View) 계층에서 안전하게 수행됩니다.



```mermaid
sequenceDiagram
    autonumber
    actor User as 사용자
    participant App as App (UI)
    participant Scanner as MarketScanner (Controller)
    participant Fetcher as DataFetcher (Data)
    participant Strategy as Strategies (Model)
    participant Formatter as Formatters (View)

    User->>App: 중앙 '스캔 시작' 버튼 클릭 (UX 개선)
    App->>Scanner: run_scan(tickers=200개) 호출
    
    loop 200개 종목 멀티스레딩 처리
        Scanner->>Fetcher: get_and_process_data(ticker)
        alt 정상 데이터
            Fetcher-->>Scanner: DataFrame 반환
            Scanner->>Strategy: analyze(df)
            
            Note over Strategy: [버그픽스] P2: 이격도 임계값 비교<br/>-> "초기포착" or "추세확정" 상태 부여
            
            Strategy-->>Scanner: Result Dictionary 반환
        else 예외 발생 (API 오류, 상장폐지 등)
            Fetcher-->>Scanner: Exception 발생
            Note over Scanner: [버그픽스] 조용히 누락(Silent Drop)시키지 않고<br/>Failure 리스트에 명시적 추가
        end
    end

    Note over Scanner: 무결성 검증: Success + Failures == 200
    Scanner-->>App: {results: [..], failures: [..]} 반환

    App->>Formatter: format_p1(results)
    Note over Formatter: [버그픽스] 기여점수 기준 정렬 후<br/>상위 5개(Top 5)만 슬라이싱
    Formatter-->>App: P1 DataFrame (Top 5) 반환
    
    App->>Formatter: format_p2, format_p3 호출
    Formatter-->>App: 포맷팅된 DataFrame 반환
    
    App-->>User: P1/P2/P3 및 분석 실패 리스트 화면 렌더링

```

---

### 2. 정적 모델링: 클래스 다이어그램 (Class Diagram)

Hotfix V4.2 패치가 적용된 시스템의 정적 구조입니다. 각 클래스가 단일 책임 원칙(SRP)을 준수하도록 책임을 명확히 분리했습니다.

* **설계 포인트:**
* **의존성 역전 원칙 (DIP):** `MarketScanner`는 구체적인 전략 클래스(`P1`, `P2`)를 알지 못하고, 추상화된 `SectorAnalysisStrategy` 인터페이스에만 의존합니다.
* **뷰 필터 패턴 (View Filter):** `format_p1` 함수에 `limit` 파라미터(또는 내부 로직)를 추가하여 View 레벨에서 데이터를 가공합니다.



```mermaid
classDiagram
    class StreamlitUI {
        +select_date() date
        +click_main_scan() bool
        +render_results(results, failures)
    }
    note for StreamlitUI "UI 배치 변경\n(메인 중앙 스캔 버튼)"

    class MarketScanner {
        -data_fetcher: DataFetcher
        -strategies: List~SectorAnalysisStrategy~
        +run_scan(tickers) Dict
        -process_stock(ticker) Dict
    }
    note for MarketScanner "200개 무결성 보장\n(Failures 이탈 방지)"

    class DataFetcher {
        -kis_client: KisClient
        +get_and_process_data(ticker) DataFrame
    }

    class SectorAnalysisStrategy {
        <<interface>>
        +analyze(df: DataFrame) Dict
    }

    class P1Strategy {
        +analyze(df) Dict
    }
    
    class P2Strategy {
        -calculate_disparity_state(value) str
        +analyze(df) Dict
    }
    note for P2Strategy "P2 추세확정 판단 로직 추가\n(이격도 임계값 캡슐화)"

    class Formatters {
        <<module>>
        +format_p1(results: DataFrame, limit: int=5) DataFrame
        +format_p2(results: DataFrame) DataFrame
        +format_p3(results: DataFrame) DataFrame
    }
    note for Formatters "P1 뷰어 제한 로직 추가\n(Top 5 Slicing)"

    StreamlitUI --> MarketScanner : 호출
    StreamlitUI --> Formatters : 결과 렌더링 위임
    MarketScanner --> DataFetcher : 데이터 요청
    MarketScanner --> SectorAnalysisStrategy : 분석 위임
    SectorAnalysisStrategy <|-- P1Strategy
    SectorAnalysisStrategy <|-- P2Strategy

```
