
import streamlit as st
import pandas as pd
import re

st.title("📚 중복 도서 탐지기 (개선된 초기 버전)")

uploaded_file = st.file_uploader("엑셀 파일 업로드 (성명, 독서활동상황 열 필수)", type=["xlsx", "csv"])

def clean_title(text):
    # 괄호 안 제거 + 공백 제거 + 특수문자 제거 + 소문자 통일
    title = re.sub(r'\([^)]*\)', '', str(text))
    title = re.sub(r'\s+', '', title)
    title = re.sub(r'[^\w가-힣]', '', title)
    return title.strip().lower()

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # 열 이름 공백 제거
        df.columns = df.columns.str.replace(r'\s+', '', regex=True)

        if '성명' not in df.columns or '독서활동상황' not in df.columns:
            st.error("❗ '성명'과 '독서활동상황' 열이 필요합니다.")
        else:
            df = df[['성명', '독서활동상황']]
            df['성명'] = df['성명'].ffill()  # 빈 셀 위로 채우기
            df = df.dropna(subset=['독서활동상황'])

            # 도서명 분리
            df['도서목록'] = df['독서활동상황'].str.split(',')
            df = df.explode('도서목록').reset_index(drop=True)

            df['정리된도서명'] = df['도서목록'].apply(clean_title)

            # 정확 중복 여부 판단
            df['정확중복여부'] = df.duplicated(subset=['성명', '정리된도서명'], keep=False).map({True: '⭕', False: '❌'})

            st.success("✅ 중복 도서 분석 완료!")
            st.dataframe(df[['성명', '도서목록', '정리된도서명', '정확중복여부']])

            # 다운로드
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 결과 다운로드 (CSV)",
                data=csv,
                file_name='중복도서_개선초기버전.csv',
                mime='text/csv',
            )

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
