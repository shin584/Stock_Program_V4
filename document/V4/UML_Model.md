1. 클래스 다이어그램 (Class Diagram)

classDiagram
    %% MVC: View
    class StreamlitUI {
        +select_date()
        +click_scan()
        +render_results(results, sectors, failures)
    }

    %% MVC: Controller
    class MarketScanner {
        -data_fetcher: DataFetcher
        -strategies: List~SectorAnalysisStrategy~
        +run_scan(date)
        +aggregate_top_sectors(results)
        -handle_exceptions(error)
    }

    %% MVC: Model (Data & API)
    class DataFetcher {
        -kis_client: KisClient
        +get_and_process_data(ticker) DataFrame
        -calculate_indicators(df) DataFrame
    }

    class KisClient {
        <<Singleton>>
        -_instance: KisClient$
        -access_token: String
        +get_instance()$ KisClient
        +fetch_market_data(ticker) JSON
        +refresh_token()
    }

    %% Strategy Pattern (Business Logic)
    class SectorAnalysisStrategy {
        <<Interface>>
        +analyze(df: DataFrame) Dict
    }

    class P1Strategy {
        +analyze(df: DataFrame) Dict
    }
    class P2Strategy {
        +analyze(df: DataFrame) Dict
    }
    class P3Strategy {
        +analyze(df: DataFrame) Dict
    }

    %% Relationships
    StreamlitUI --> MarketScanner : "1. 스캔 요청"
    MarketScanner --> DataFetcher : "2. 데이터 수집/전처리 지시"
    DataFetcher --> KisClient : "3. API 호출"
    MarketScanner o-- SectorAnalysisStrategy : "4. 분석 위임 (의존성 주입)"
    
    SectorAnalysisStrategy <|.. P1Strategy : "Implements"
    SectorAnalysisStrategy <|.. P2Strategy : "Implements"
    SectorAnalysisStrategy <|.. P3Strategy : "Implements"

2. 시퀀스 다이어그램 (Sequence Diagram)

sequenceDiagram
    autonumber
    actor User as 개인 투자자
    participant UI as 대시보드 UI (View)
    participant Controller as MarketScanner (Controller)
    participant Data as DataFetcher (Model)
    participant API as KIS API (Singleton)
    participant Strategy as SectorAnalysisStrategy

    User->>UI: 분석 기준일 선택
    User->>UI: '종목 스캔' 버튼 클릭
    UI->>Controller: 스캔 시작 및 분석 요청

    loop 대상 종목 리스트 순회 (Multi-threading)
        Controller->>API: 시세 및 매매동향 데이터 요청
        
        alt 3a. 토큰 만료 시
            API-->>Controller: Error: 인증 실패
            Controller->>API: 새 토큰 갱신 요청
            API-->>Controller: Success: 발급 완료
            Controller->>API: 데이터 재요청
        else 3b. Rate Limit 초과 시
            API-->>Controller: Error: 호출 한도 초과
            Controller->>Controller: 지수 백오프 대기 후 재요청
        else 3c. 휴장일인 경우
            API-->>Controller: Error: 해당 일자 데이터 없음
            Controller-->>UI: 스캔 중단 신호 반환
            UI-->>User: "시장 휴장일입니다" 알림 표시
        end

        API-->>Data: Raw JSON 데이터 반환
        
        Data->>Data: 정형화(DataFrame) 및 보조지표(MA, MACD) 계산
        
        alt 3d. 데이터 부족 시
            Data-->>Controller: Exception: 데이터 부족
            Controller->>Controller: Failures 리스트에 종목 기록 후 스킵 (Continue)
        else 정상 처리 시
            Data-->>Strategy: 전처리된 DataFrame 전달
            Strategy->>Strategy: P1, P2, P3 조건 부합 여부 검사 (Rule 1~3)
            Strategy-->>Controller: 종목별 분석 결과(Score/Priority) 반환
        end
    end

    Controller->>Controller: 상위 3개 주도 섹터 집계 (Rule 4)
    Controller-->>UI: 필터링된 종목 리스트 및 섹터 집계 결과 반환
    UI-->>User: 종목 리스트 및 주도 섹터 카드 시각화 렌더링