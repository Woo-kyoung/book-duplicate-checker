import streamlit as st
import pandas as pd
import re

st.title("📚 중복 도서 탐지기 (작가명 뒤 쉼표만 분리)")

uploaded_file = st.file_uploader("엑셀 파일을 업로드 해주세요", type=["xlsx"])

# 도서명 분리 함수 (작가명 뒤 쉼표만 분리)
def split_books(text):
    if pd.isna(text):
        return []
    segments = re.split(r'\([^)]*\)\s*,\s*', text)
    cleaned_books = [re.sub(r'\([^)]*\)', '', seg).strip() for seg in segments if seg.strip()]
    return cleaned_books

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # 필수 컬럼이 포함되어 있는지 확인
    required_columns = {"번호", "성명", "과목", "학년도", "학년", "학기", "독서활동상황"}
    if not required_columns.issubset(df.columns):
        st.error("엑셀 파일에 필수 열이 포함되어 있지 않습니다. 다음 열이 필요합니다: " + ", ".join(required_columns))
    else:
        # 도서명 추출
        df['도서목록'] = df['독서활동상황'].apply(split_books)
        exploded = df.explode('도서목록').dropna(subset=['도서목록'])

        # 도서명별 중복 여부 판단
        duplicated = exploded.duplicated(subset=['성명', '도서목록'], keep=False)
        exploded['중복여부'] = duplicated.map({True: '⭕', False: '❌'})

        st.success("분석 완료! 아래에서 결과를 확인하세요.")
        st.dataframe(exploded[['번호', '성명', '도서목록', '중복여부']])

        # 다운로드 기능
        def convert_df(df):
            return df.to_excel(index=False, engine='openpyxl')

        st.download_button(
            label="📥 결과 엑셀 다운로드",
            data=convert_df(exploded),
            file_name='중복도서_분석결과.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
