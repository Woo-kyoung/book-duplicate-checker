import streamlit as st
import pandas as pd
import re
from difflib import SequenceMatcher

# 도서명 분리
def split_books(text):
    segments = re.split(r'\([^)]*\)\s*,\s*', str(text))
    cleaned = [re.sub(r'\([^)]*\)', '', seg).strip() for seg in segments if seg.strip()]
    return cleaned

# 도서명 정리: 공백, 특수문자 제거 + 소문자 통일
def normalize_title(title):
    title = re.sub(r'\s+', '', str(title))
    title = re.sub(r'[^\w가-힣]', '', title)
    return title.lower()

# 유사도 판단 함수
def is_similar(a, b, threshold=0.9):
    return SequenceMatcher(None, a, b).ratio() >= threshold

# 도서 데이터 처리
def process_book_data(df):
    df.columns = df.columns.str.replace(r'\s+', '', regex=True)  # 열 이름 공백 제거
    df['도서목록'] = df['독서활동상황'].apply(split_books)
    exploded = df.explode('도서목록').reset_index(drop=True)
    exploded['정리된도서명'] = exploded['도서목록'].apply(normalize_title)

    exploded['정확중복여부'] = exploded.duplicated(subset=['성명', '정리된도서명'], keep=False).map({True: '⭕', False: '❌'})

    similar_flags = []
    recommendations = []
    for i, row_i in exploded.iterrows():
        found_similar = False
        best_match = ''
        highest_ratio = 0
        for j, row_j in exploded.iterrows():
            if i != j and row_i['성명'] == row_j['성명']:
                ratio = SequenceMatcher(None, row_i['정리된도서명'], row_j['정리된도서명']).ratio()
                if ratio >= 0.9:
                    found_similar = True
                if ratio > highest_ratio:
                    highest_ratio = ratio
                    best_match = row_j['도서목록']
        similar_flags.append('⭕' if found_similar else '❌')
        recommendations.append(best_match if highest_ratio >= 0.85 else '')
    
    exploded['유사중복여부'] = similar_flags
    exploded['가장유사한도서추천'] = recommendations

    return exploded[['성명', '도서목록', '정리된도서명', '정확중복여부', '유사중복여부', '가장유사한도서추천']]

# Streamlit UI
st.title("📚 중복 도서 탐지기 (최종 버전: 공백 허용)")

uploaded_file = st.file_uploader("엑셀 또는 CSV 파일 업로드", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # 열 이름 공백 제거 (핵심 처리)
        df.columns = df.columns.str.replace(r'\s+', '', regex=True)

        if '성명' not in df.columns or '독서활동상황' not in df.columns:
            st.error("⚠️ 필수 열(성명, 독서활동상황)이 누락되었습니다.")
        else:
            result = process_book_data(df)
            st.success("✅ 중복 도서 분석 완료!")
            st.dataframe(result)

            csv = result.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 결과 다운로드 (CSV)",
                data=csv,
                file_name='중복도서_분석결과.csv',
                mime='text/csv',
            )

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
