import streamlit as st
import pandas as pd
from collections import Counter

st.set_page_config(page_title="539 數據臆測大師", layout="centered")
st.title("🧪 539 大數據：今晚號碼臆測模型")

@st.cache_data
def load_and_clean_data():
    url = "https://raw.githubusercontent.com/a0985122687-glitch/Lotto539-Analysis/main/history.csv"
    try:
        # 載入包含期別 (id) 的數據
        df = pd.read_csv(url)
        # 確保數字欄位轉換正確
        for col in ['id', 'n1', 'n2', 'n3', 'n4', 'n5']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.dropna().sort_values('id') # 改用「期別」排序最精準
    except:
        return pd.DataFrame()

df = load_and_clean_data()

if not df.empty:
    st.info(f"✅ 大數據分析樣本已載入：{len(df)} 期 (最後期別：{int(df['id'].max())})")
    
    st.subheader("🎯 昨晚開獎基準")
    # 讓使用者核對期別
    selected_id = st.selectbox("請確認昨晚期別：", df['id'].unique()[::-1])
    target_row = df[df['id'] == selected_id].iloc[0]
    st.write(f"📅 日期：{target_row['date']} | 獎號：{int(target_row['n1']):02d}, {int(target_row['n2']):02d}, {int(target_row['n3']):02d}, {int(target_row['n4']):02d}, {int(target_row['n5']):02d}")

    # 臆測邏輯
    st.divider()
    st.subheader("🔮 根據此期別之今晚臆測")
    last_nums = [target_row['n1'], target_row['n2'], target_row['n3'], target_row['n4'], target_row['n5']]
    
    pool = []
    total_rows = len(df)
    for i in range(total_rows - 1):
        current_set = set(df.iloc[i][['n1','n2','n3','n4','n5']].values)
        matches = len(current_set.intersection(set(last_nums)))
        if matches >= 1:
            next_issue = df.iloc[i+1][['n1','n2','n3','n4','n5']].values
            # 匹配數越高，權重越高
            for _ in range(matches * 2):
                pool.extend(next_issue)
    
    if pool:
        suggestions = Counter(pool).most_common(5)
        cols = st.columns(5)
        for idx, (num, val) in enumerate(suggestions):
            cols[idx].metric(f"臆測 {idx+1}", f"{int(num):02d}", f"強度 {val}")
    else:
        st.warning("數據庫中尚未發現此期號碼的連動規律。")
else:
    st.error("請確保 history.csv 第一行是 id,date,n1,n2,n3,n4,n5")
