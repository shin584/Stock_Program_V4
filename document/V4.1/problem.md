1. streamlit 화면 상에서 p1/p2/p3가 칼럼이 나뉘긴 했지만 p2,p3 종목이 보이지 않음
- v3 코드를 분석하여 원인 파악

**V3 구현 흐름**
V3는 아래 순서입니다.

1. [legacy kis_client.py](/c:/project/SW_assignment/legacy_code/stock_v3/api/kis_client.py)
   - `get_chart_price()`로 기간별 일봉 시세 조회
   - API:
     ```text
     inquire-daily-itemchartprice
     ```
   - `output2`로 여러 일자 row를 받음
   - `get_investor_trend()`로 일별 투자자 수급 조회

2. [legacy data_fetcher.py](/c:/project/SW_assignment/legacy_code/stock_v3/core/data_fetcher.py)
   - 기본 `days=100`, pipeline에서는 `days=60`
   - 차트 데이터와 투자자 데이터를 `일자` 인덱스로 join
   - `종가`, `거래량`, `거래대금`, `등락률`, 외국인/기관 순매수 금액을 같은 DataFrame에 만듦
   - 투자자 순매수 금액 컬럼에 단위 보정 수행:
     ```python
     amount * 1000000
     ```

3. [legacy pipeline.py](/c:/project/SW_assignment/legacy_code/stock_v3/core/pipeline.py)
   - 종목마다:
     ```text
     get_stock_data(ticker, days=60)
     -> calculate_indicators(df)
     -> strategy.analyze(df)
     ```
   - 즉 P2/P3는 60일 일봉 + 수급 + 지표가 있는 DataFrame으로 판단

4. [legacy strategy.py](/c:/project/SW_assignment/legacy_code/stock_v3/core/strategy.py)
   - P2는 최근 5일, 20일 MA, 외국인/기관 연속 매수일을 사용
   - P3는 전일/당일 거래량을 비교

---

## 현재 V4와의 핵심 차이

### 1. 가격 데이터 조회 API가 다름
현재 [kis_client.py](/c:/project/SW_assignment/Stock_Program_V4/api/kis_client.py)의 `fetch_market_data()`는 가격을 이렇게 가져옵니다.

```text
inquire-price
```

이건 현재가 조회 중심입니다.

반면 V3 P2/P3 경로는:

```text
inquire-daily-itemchartprice
```

를 써서 **여러 일자 일봉**을 가져옵니다.

이 차이가 가장 큽니다.

### 2. V4 DataFetcher가 P2/P3용 시계열 DataFrame을 안정적으로 만들지 못함
현재 [data_fetcher.py](/c:/project/SW_assignment/Stock_Program_V4/core/data_fetcher.py)는:

```text
price payload
+ investor payload
-> merge
-> indicators
```

를 하지만 가격 payload가 현재가 단건이면:
- P2의 5일/20일 조건이 약해짐
- P3의 전일 거래량 비교가 불가능하거나 빈약해짐
- 일자 기준 가격/수급 결합도 V3와 달라짐

### 3. 투자자 순매수 금액 단위 보정 차이
V3 데이터 전처리에는 이 로직이 있습니다.

```python
df_inv[amount_col] = df_inv[amount_col] * 1000000
```

현재 V4 DataFetcher는 숫자 변환만 하고 금액 단위 보정은 하지 않습니다.

이게 중요합니다.  
P2는 아래 규모 조건을 씁니다.

- 최근 5일 누적 100억 이상
- 당일 30억 이상

수급 금액 단위가 V3처럼 백만원 단위로 내려오는데 V4가 `* 1_000_000` 보정을 안 하면, P2 규모 조건이 거의 실패할 수 있습니다.

### 4. 테스트와 실데이터 전제가 다름
현재 전략 테스트는 P2/P3가 통과하도록 Mock DataFrame을 충분히 길게 만듭니다.

- P2: 20개 row
- P3: 여러 row
- 외국인/기관 수급 값도 임계치 이상

하지만 실스캔 경로는 그 DataFrame 전제를 충족하지 못하고 있습니다.

---

# 수정안

## 1순위: V4 KIS 가격 조회 경로를 V3처럼 기간 일봉 기반으로 복원
현재 V4의 `fetch_market_data()`가 가격 부분에서 `inquire-price`만 쓰는 구조를 바꿔야 합니다.

수정 방향:
- `KisClient`에 V3의 `get_chart_price()`에 해당하는 기간별 일봉 조회 메서드 추가 또는 `fetch_market_data()` 내부 가격 조회를 차트 조회로 변경
- 조회 API:
  ```text
  /uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice
  ```
- 최소 60일 이상 일봉 row 확보

## 2순위: V4 DataFetcher를 V3 데이터 조립 방식으로 맞춤
수정 방향:
- 가격 일봉 `output2`를 DataFrame화
- 투자자 동향 `output`을 DataFrame화
- 둘 다 `stck_bsop_date`를 `일자`로 변환
- 날짜 인덱스로 join
- `등락률`이 없으면 종가 pct_change로 계산
- MA/MACD 계산은 현재 V4 방식 유지 가능

## 3순위: 투자자 금액 단위 보정 확인 및 복원
V3처럼 투자자 금액 컬럼에 단위 보정이 필요합니다.

대상:
- 개인 순매수 금액
- 외국인 순매수 금액
- 기관 순매수 금액

수정 후보:
```text
amount column * 1_000_000
```

이 부분이 빠지면 P2 규모 필터가 실데이터에서 거의 실패할 수 있습니다.

## 4순위: V4 스캐너는 현재 구조 유지 가능
[market_scanner.py](/c:/project/SW_assignment/Stock_Program_V4/core/market_scanner.py)의:
- DI
- 멀티스레딩
- 실패 종목 격리
- P1/P2/P3 결과 플래그 분리

이 구조는 유지해도 됩니다.

문제는 스캐너가 아니라 **스캐너가 전략에 넘기는 DataFrame의 내용**입니다.

---

## 요약 비교

| 항목 | V3 | 현재 V4 | 영향 |
|---|---|---|---|
| 가격 조회 | 기간 일봉 차트 | 현재가 단건 중심 | P2/P3 입력 부족 |
| 가격 row 수 | 약 60일 | 매우 적거나 단건 | MA/거래량 비교 약화 |
| 수급 결합 | 일자 join | 현재가 payload와 결합 | 연속 수급 판단 불안정 |
| 수급 금액 단위 | `* 1_000_000` 보정 | 보정 없음 | P2 규모 필터 실패 가능 |
| P1 | 단건도 가능 | 가능 | 화면에 잘 뜸 |
| P2/P3 | 시계열 필요 | 시계열 부족 | 화면에서 비기 쉬움 |

**가장 우선적인 수정안은 `KisClient + DataFetcher`를 V3의 “60일 일봉 + 일별 수급 결합” 흐름으로 복원하는 것입니다.**  
UI 포맷터 분리 문제라기보다, 실전략 입력 데이터가 V3 수준으로 복원되지 않은 것이 본질입니다.

