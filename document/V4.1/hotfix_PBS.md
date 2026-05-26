[Stock_Program_V4.1] Hotfix PBS 명세서
🩹 [PBS-Hotfix] 데이터 병합 충돌 해결 (Join Overlap Fix)
Target: core/data_fetcher.py

설명: API 응답에 포함된 매핑되지 않은 공통 컬럼(예: prdy_vrss_sign)들이 rename 이후에도 남아있어 join 시 충돌하는 문제를 방지합니다.

[Prompt Template - 복사해서 사용하세요]

Plaintext
당신은 Pandas 데이터 엔지니어링에 능숙한 시니어 개발자입니다. 현재 `data_fetcher.py`에서 두 API의 응답을 DataFrame으로 만든 뒤 `join`하는 과정에서, KIS 원본 컬럼(`prdy_vrss` 등)이 양쪽에 남아있어 `ValueError: columns overlap but no suffix specified` 오류가 발생하고 전체 스캔이 실패하고 있습니다. 이를 해결하기 위해 다음 지침에 따라 코드를 수정하십시오.

[수정 지침]
1. `_merge_frames` 함수 방어 로직 추가: 
   `price_df.join(investor_df, how="left")` 부분에 `rsuffix='_inv'` (또는 `lsuffix`) 파라미터를 명시적으로 추가하여, 이름이 겹치는 잔여 컬럼이 있더라도 충돌 없이 안전하게 병합되도록 방어적 프로그래밍을 적용하십시오.
2. (선택적 최적화) 가비지 컬럼 제거: 
   `_build_price_frame`과 `_build_investor_frame` 내에서 `