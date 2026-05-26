V4

1. p1/p2/p3가 분리되지 않음.

ex)
P1: 지수 주도주 (Index Leaders)
ticker | name | 현재가 | 등락률 | contrbution | 외국인 순매수 | 기관순매수
0	005930	삼성전자	299,500원	8.51%	58971175.6억	10954.3억	7728.8억
1	000660	SK하이닉스	1,940,000원	11.17%	48730267.2억	-7816.8억	14052.8억
2	012330	현대모비스	670,000원	25.23%	8196459.3억	-988.7억	1109.2억
3	005380	현대차	666,000원	12.50%	7320090.1억	772.7억	579.9억
4	402340	SK스퀘어	1,179,000원	14.58%	6440691.0억	-768.6억	1299.2억

P2: 수급 주도주 (Supply Leaders)
ticker | name | 단계 | 포착사유
114	347850	디앤디파마텍	초기포착	외인주도(6일)	0	6	3.23%
143	476830	알지노믹스	초기포착	외인주도(6일)	0	6	2.36%
84	078930	GS	초기포착	외인주도(6일)	0	6	2.03%
157	095610	테스	추세확정	기관주도(4일)	4	0	3.18%
155	096530	씨젠	추세확정	외인주도(3일) / 쌍끌이	1	3	2.68%

P3: 급등 전조 (Volume Spike + Consolidation)
ticker | name | 현재가 | 등락률 | vol surge | 외국인순매수 | 기관순매수
84	078930	GS	75,400원	2.03%	Vol Surge +59.0%	106.3억	-83.6억
148	115180	큐리언트	27,450원	4.37%	Vol Surge +89.1%	-7.0억	-15.2억
157	095610	테스	120,100원	3.18%	Vol Surge +57.8%	-14.3억	85.0억
161	290650	엘앤씨바이오	63,200원	0.96%	Vol Surge +62.3%	63.3억	6.8억

2. 코스닥 종목이 집계되지 않음

### 분석

1. P1/P2/P3가 분리되지 않는 원인
현재 market_scanner.py는 P1/P2/P3 결과를 각각 별도 목록으로 만들지 않고, 한 종목 결과 안에 아래처럼 플래그로 합쳐서 반환합니다.
text



is_p1
is_p2
is_p3
p1_result
p2_result
p3_result

그리고 app.py는 render_results()에서 “선별 종목” 테이블 하나만 렌더링합니다. 즉 UI에 P1: 지수 주도주, P2: 수급 주도주, P3: 급등 전조 섹션을 나누는 로직이 없습니다.
또한 formatters.py도 format_results()에서 공통 컬럼과 P1/P2/P3 여부만 표시합니다. P2의 단계, 포착사유, P3의 vol surge, 외국인/기관 순매수 같은 전용 표시 컬럼을 펼치지 않습니다.
정리하면, 분석 로직은 P1/P2/P3 플래그를 만들지만, 컨트롤러와 UI가 결과를 세 갈래로 분리해서 ViewModel을 만들지 않기 때문에 현재는 한 테이블에 합쳐져 보이는 구조입니다.
2. 코스닥 종목이 집계되지 않는 원인
데이터 자체에는 KOSDAQ이 있습니다. 확인 결과:
text



전체 350개
KOSPI 200개
KOSDAQ 150개

문제는 app.py에서 시장 선택이 단일 선택입니다.
python



market_type = st.sidebar.selectbox(... options=["KOSPI", "KOSDAQ"])
tickers = load_tickers(market_type=market_type, top_n=int(top_n))

즉 사용자가 KOSPI를 선택하면 load_tickers()가 KOSPI만 필터링합니다. KOSPI와 KOSDAQ을 합쳐서 스캔하는 흐름이 없습니다. 레거시 예시는 KOSPI와 KOSDAQ을 각각 스캔한 뒤 합치는 구조였는데, V4 UI는 현재 단일 시장만 스캔합니다.
추가로 tickers.json에는 sector 컬럼이 없습니다.
text



keys: cap, code, market, name
has_sector: False

그래서 market_scanner.py는 섹터가 없으면 "UNKNOWN"으로 넣습니다. 이 상태에서는 “주도 섹터 집계”도 실제 업종별 집계가 아니라 전부 UNKNOWN으로 묶일 가능성이 큽니다.
결론:
P1/P2/P3 미분리: 결과 ViewModel/UI가 전략별로 나뉘어 있지 않음.
KOSDAQ 누락: UI가 KOSPI/KOSDAQ 중 하나만 스캔함.
섹터 집계 부정확: tickers.json에 sector 컬럼이 없음.