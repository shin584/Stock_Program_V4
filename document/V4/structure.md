파일 작성 없이, PBS 0~5 완료 시 예상되는 폴더/파일 구조도는 아래처럼 잡으면 됩니다.

```text
Stock_Program_V4/
├─ README.md
├─ secrets.json                         # 로컬 인증 정보, git 제외 권장
├─ tickers.json                         # 스캔 대상 종목 목록
│
├─ api/
│  ├─ __init__.py
│  └─ kis_client.py                     # PBS-1: KIS API 통신, Singleton, 토큰/재시도 처리
│
├─ core/
│  ├─ __init__.py
│  ├─ config.py                         # PBS-0: 설정 로드, ConfigError, Fail-Fast 검증
│  ├─ data_fetcher.py                   # PBS-2: JSON → DataFrame 전처리, MA/MACD 계산
│  ├─ strategy.py                       # PBS-3: P1/P2/P3 Strategy Pattern 분석 로직
│  ├─ market_scanner.py                 # PBS-4: DI 기반 스캔 컨트롤러, 실패 종목 수집, 섹터 집계
│  └─ utils.py                          # PBS-4: tickers.json 로드 등 유틸리티 함수
│
├─ ui/
│  ├─ __init__.py
│  └─ app.py                            # PBS-5: Streamlit UI, Composition Root
│
├─ tests/
│  ├─ __init__.py
│  └─ test_strategy.py                  # PBS-3: P1/P2/P3 단위 테스트
│
└─ document/
   ├─ PBS.md
   ├─ PBS_UPDATE.md
   ├─ UML_Model.md
   ├─ Use_Case_Text.md
   ├─ refactoring_project_draft.md
   ├─ regacy_summary.md
   ├─ rule.md
   └─ rule4.md
```

PBS별 책임 흐름은 이렇게 연결됩니다.

```text
ui/app.py
  └─ MarketScanner
      ├─ DataFetcher
      │   └─ KisClient Singleton
      ├─ P1Strategy
      ├─ P2Strategy
      └─ P3Strategy
```

즉, `app.py`는 객체들을 조립하고 화면만 담당하고, 실제 데이터 수집은 `DataFetcher`, API 통신은 `KisClient`, 분석 규칙은 `strategy.py`, 전체 스캔 흐름은 `market_scanner.py`가 맡는 구조입니다.