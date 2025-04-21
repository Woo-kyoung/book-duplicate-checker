
import streamlit as st
import pandas as pd

st.set_page_config(page_title="중복 도서 탐지기", layout="wide")
st.title("📚 중복 도서 탐지기")
st.markdown("엑셀 파일을 업로드하면 학생별로 중복된 도서가 있는지 자동으로 탐지합니다.")

uploaded_file = st.file_uploader("엑셀 파일 업로드 (예: 2-1 독서.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=None)
        df_data = df.iloc[1:, [1, 4, 5, 6]]  # 성명, 학년, 학기, 도서목록
        df_data.columns = ["성명", "학년", "학기", "도서목록"]

        df_data = df_data.fillna(method="ffill")
        df_data["도서목록"] = df_data["도서목록"].astype(str).str.split(",")
        df_exploded = df_data.explode("도서목록")
        df_exploded["도서목록"] = df_exploded["도서목록"].str.strip()

        df_valid = df_exploded[df_exploded["도서목록"].str.contains(r"\(.+\)")]
        df_valid = df_valid.sort_values(by=["학년", "성명"])

        st.subheader("✅ 학생별 정리된 독서 목록")
        st.dataframe(df_valid, use_container_width=True)

        # 중복 탐지
        dup = (
            df_valid.groupby(["성명", "학년", "학기", "도서목록"])
            .size()
            .reset_index(name="count")
        )
        dup = dup[dup["count"] >= 2]

        st.subheader("⚠️ 중복된 도서 목록")
        if not dup.empty:
            st.dataframe(dup, use_container_width=True)
            csv = dup.to_csv(index=False).encode("utf-8-sig")
            st.download_button("중복 도서 목록 다운로드", csv, file_name="중복_도서_목록.csv")
        else:
            st.success("중복된 도서가 없습니다! 🎉")

    except Exception as e:
        st.error(f"파일 처리 중 오류 발생: {e}")
