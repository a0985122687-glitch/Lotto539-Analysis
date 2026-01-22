import streamlit as st
import pandas as pd
from collections import Counter

st.set_page_config(page_title="539 數據建模專家", layout="centered")
st.title("🧪 539 今晚預測建模 (大數據版)")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/a0985122687-glitch/Lotto539-Analysis/main/history.csv"
    try:
        # 增加容錯處理，確保只讀取前 6 欄
        df = pd.read_csv(url, usecols=['date','n1','n2','n3','n4','n5'])
        return df.sort_values('date')
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    sample_size = len(df)
    st.info(f"✅ 大數據分析樣本已載入：{sample_size} 期")
    
    # 核心臆測邏輯
    st.subheader("🎯 昨晚開獎號碼 (預測基準)")
    last_nums = st.multiselect("請選出昨晚的 5 個號碼：", range(1, 40), max_selections=5)
    
    if len(last_nums) == 5:
        st.divider()
        st.subheader("🔮 今晚臆測建議")
        
        # 1. 拖牌關聯分析
        pool = []
        for i in range(sample_size - 1):
            current = set(df.iloc[i][['n1','n2','n3','n4','n5']].values)
            match_count = len(current.intersection(set(last_nums)))
            if match_count >= 1: # 只要有中一個號碼，就紀錄下一期
                next_issue = df.iloc[i+1][['n1','n2','n3','n4','n5']].values
                # 匹配越多，權重越高
                for _ in range(match_count):
                    pool.extend(next_issue)
        
        if pool:
            suggestions = Counter(pool).most_common(5)
            cols = st.columns(5)
            for idx, (num, val) in enumerate(suggestions):
                cols[idx].metric(f"推薦 {idx+1}", f"{int(num):02d}", f"關聯強度 {val}")
        
        # 2. 近期熱度補強
        st.write("---")
        recent_30 = df.tail(30)[['n1','n2','n3','n4','n5']].values.flatten()
        hot_30 = [f"{int(n):02d}" for n, c in Counter(recent_30).most_common(5)]
        st.success(f"🔥 近期 30 期強勢號碼參考：{', '.join(hot_30)}")
else:
    st.error("數據格式不對，請確保 history.csv 第一行是 date,n1,n2,n3,n4,n5")
