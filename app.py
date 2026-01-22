import streamlit as st
import pandas as pd
from collections import Counter

st.set_page_config(page_title="539 數據臆測大師", layout="centered")
st.title("🧪 539 大數據：今晚號碼臆測模型")

@st.cache_data
def load_clean_data():
    url = "https://raw.githubusercontent.com/a0985122687-glitch/Lotto539-Analysis/main/history.csv"
    try:
        # 讀取 CSV，如果逗號不對，自動嘗試用空格/多個空格拆解
        df = pd.read_csv(url, sep=r'\s|,', engine='python', on_bad_lines='skip')
        # 重新強制設定標頭，確保對齊
        df.columns = ['id', 'date', 'n1', 'n2', 'n3', 'n4', 'n5']
        # 轉換為數字
        for col in ['id', 'n1', 'n2', 'n3', 'n4', 'n5']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.dropna().sort_values('id')
    except Exception as e:
        return pd.DataFrame()

df = load_clean_data()

if not df.empty:
    st.info(f"✅ 大數據樣本已載入：{len(df)} 期 (最後期別：{int(df['id'].max())})")
    
    st.subheader("🎯 昨晚開獎基準 (核對期別)")
    selected_id = st.selectbox("請確認昨晚期別：", df['id'].unique()[::-1])
    target = df[df['id'] == selected_id].iloc[0]
    
    current_nums = [int(target['n1']), int(target['n2']), int(target['n3']), int(target['n4']), int(target['n5'])]
    st.success(f"📅 期別：{int(target['id'])} | 獎號：{', '.join([f'{n:02d}' for n in current_nums])}")

    st.divider()
    st.subheader("🔮 根據此期別之今晚臆測")
    pool = []
    df_list = df.sort_values('id').values.tolist()
    for i in range(len(df_list) - 1):
        # 提取該行的號碼 (索引 2 到 6)
        row_nums = set(df_list[i][2:7])
        matches = len(row_nums.intersection(set(current_nums)))
        if matches >= 1:
            next_nums = df_list[i+1][2:7]
            for _ in range(matches * 2):
                pool.extend(next_nums)
    
    if pool:
        suggestions = Counter(pool).most_common(5)
        cols = st.columns(5)
        for idx, (num, val) in enumerate(suggestions):
            cols[idx].metric(f"臆測 {idx+1}", f"{int(num):02d}", f"強度 {val}")
else:
    st.error("請檢查 history.csv，確保內容包含逗號分割。")
