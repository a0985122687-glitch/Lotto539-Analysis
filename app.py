import streamlit as st
import pandas as pd
from collections import Counter

st.set_page_config(page_title="539 數據臆測大師", layout="centered")
st.title("🧪 539 大數據：今晚號碼臆測模型")

@st.cache_data
def load_clean_data():
    url = "https://raw.githubusercontent.com/a0985122687-glitch/Lotto539-Analysis/main/history.csv"
    try:
        # 指定欄位名稱，確保讀取正確
        df = pd.read_csv(url, sep=',', on_bad_lines='skip')
        # 確保期別與號碼皆為數字
        for col in ['id', 'n1', 'n2', 'n3', 'n4', 'n5']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.dropna().sort_values('id')
    except Exception as e:
        st.error(f"資料讀取失敗: {e}")
        return pd.DataFrame()

df = load_clean_data()

if not df.empty:
    sample_size = len(df)
    st.info(f"✅ 大數據樣本已載入：{sample_size} 期 (最後期別：{int(df['id'].max())})")
    
    st.subheader("🎯 昨晚開獎基準 (對期別)")
    # 讓使用者從期別選單選擇基準點
    selected_id = st.selectbox("請確認昨晚期別：", df['id'].unique()[::-1])
    target = df[df['id'] == selected_id].iloc[0]
    
    # 顯示該期號碼供核對
    current_nums = [int(target['n1']), int(target['n2']), int(target['n3']), int(target['n4']), int(target['n5'])]
    st.success(f"📅 期別：{int(target['id'])} | 獎號：{', '.join([f'{n:02d}' for n in current_nums])}")

    # 臆測邏輯：拖牌分析
    st.divider()
    st.subheader("🔮 根據此期別之今晚臆測")
    pool = []
    for i in range(len(df) - 1):
        issue_set = set(df.iloc[i][['n1','n2','n3','n4','n5']].values)
        matches = len(issue_set.intersection(set(current_nums)))
        if matches >= 1:
            next_nums = df.iloc[i+1][['n1','n2','n3','n4','n5']].values
            for _ in range(matches * 2): # 匹配數越高權重越大
                pool.extend(next_nums)
    
    if pool:
        suggestions = Counter(pool).most_common(5)
        cols = st.columns(5)
        for idx, (num, val) in enumerate(suggestions):
            cols[idx].metric(f"臆測 {idx+1}", f"{int(num):02d}", f"強度 {val}")
else:
    st.warning("目前 history.csv 格式與 App 不符，請確保第一行是 id,date,n1,n2,n3,n4,n5")
