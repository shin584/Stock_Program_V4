

---

# [Stock_Program_V4.1] Data Pipeline 복원 PBS 명세서

## [PBS-4.1.4] KIS API 시계열 조회 복원 (가격 데이터 60일치 확보)

* **Target:** `api/kis_client.py`
* **설명:** 현재가(단건) 중심의 API 호출을 V3의 일봉 차트(시계열) API 호출로 변경하여, 전략 패턴(P2, P3)이 분석할 수 있는 충분한 과거 데이터를 확보합니다.

**[Prompt Template - 복사해서 사용하세요]**

```text
당신은 KIS API 연동에 능숙한 시니어 백엔드 개발자입니다. 현재 `fetch_market_data`가 단건 가격만 가져오고 있어 시계열 기반의 전략(MA 계산, 전일 거래량 비교)이 동작하지 않습니다. `api/kis_client.py`를 다음 지침에 따라 수정하십시오.

[수정 지침]
1. 가격 조회 엔드포인트 변경: 기존의 현재가 조회(`inquire-price`)를 기간별 일봉 차트 조회인 `/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice`로 변경하십시오.
2. Query Parameters 설정: 해당 API에 맞게 파라미터를 세팅하십시오. (예: `FID_COND_MRKT_DIV_CODE="J"`, `FID_INPUT_ISCD=ticker`, `FID_INPUT_DATE_1=시작일`, `FID_INPUT_DATE_2=종료일`, `FID_PERIOD_DIV_CODE="D"`, `FID_ORG_ADJ_PRC="0"` 등). 시작일과 종료일은 오늘 기준으로 최근 100일 정도의 데이터를 가져올 수 있도록 동적으로 계산하십시오.
3. 투자자 데이터 유지: 기존의 투자자 데이터(`inquire-investor`) 조회 로직은 그대로 유지하되, 두 API의 응답 결과를 합쳐서 반환하는 구조를 유지하십시오.
4. 예외 처리: 차트 API 호출 시 발생할 수 있는 에러를 `KisApiError`로 안전하게 감싸서 던지십시오.

```

---

## [PBS-4.1.5] DataFetcher 시계열 조립 및 금액 단위 보정

* **Target:** `core/data_fetcher.py`
* **설명:** 차트 API에서 받아온 다건의 데이터를 DataFrame으로 제대로 변환하고, 누락되었던 수급 금액 `* 1,000,000` 단위 보정을 수행합니다.

**[Prompt Template - 복사해서 사용하세요]**

```text
당신은 Pandas 데이터 가공에 능숙한 데이터 엔지니어입니다. `api/kis_client.py`가 이제 시계열 일봉 차트 데이터를 반환합니다. 이에 맞춰 `core/data_fetcher.py`를 수정하여 V3의 정교한 데이터 조립 로직을 복원하십시오.

[수정 지침]
1. `_build_price_frame` 수정: 차트 API 응답(`output2` 배열)을 처리하여 다중 행(시계열) DataFrame을 생성하도록 수정하십시오. 인덱스는 반드시 `일자`(datetime) 기준으로 오름차순 정렬되어야 합니다. 등락률(`prdy_ctrt`)이 없다면 종가 기준으로 `pct_change().mul(100)`을 수행해 안전하게 확보하십시오.
2. 금액 단위 보정 (핵심): `_build_investor_frame` 메서드 내에서, 투자자 순매수 금액 관련 컬럼(`개인_순매수금액`, `외국인_순매수금액`, `기관_순매수금액`)의 데이터에 반드시 `* 1_000_000` (백만 단위 보정)을 곱하는 전처리 로직을 추가하십시오. 이 보정이 없으면 P2 전략의 규모 필터가 실패합니다.
3. 데이터 병합: `_merge_frames`에서 가격 DataFrame과 투자자 DataFrame이 날짜(index)를 기준으로 완벽하게 `Left Join` 되도록 로직을 검증하고 필요시 보완하십시오. 빈 값은 0으로 채우십시오(fillna(0)).

```