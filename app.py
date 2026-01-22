import streamlit as st
import pandas as pd
from collections import Counter
from datetime import datetime

# 頁面設定
st.set_page_config(page_title="539 數據臆測大師", layout="centered")
st.title("🧪 539 今晚預測建模 (大數據優化版)")
st.write(f"📅 臆測基準時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}")

@st.cache_data
def load_and_clean_data():
    url = "https://raw.githubusercontent.com/a0985122687-glitch/Lotto539-Analysis/main/history.csv"
    try:
        # 只取前 6 欄，忽略雜質
        df = pd.read_csv(url, usecols=[0,1,2,3,4,5], names=['date','n1','n2','n3','n4','n5'], skiprows=1)
        df = df.dropna()
        for col in ['n1','n2','n3','n4','n5']:
            df[col] = df[col].astype(int)
        return df.sort_values('date')
    except:
        return pd.DataFrame()

df = load_and_clean_data()

if not df.empty:
    st.info(f"📊 建模樣本已載入：{len(df)} 期 (數據來源: GitHub)")
    
    # 昨晚號碼輸入
    st.subheader("🎯 昨晚開獎號碼")
    last_nums = st.multiselect("請選入昨晚的 5 個號碼：", range(1, 40), max_selections=5)
    
    if len(last_nums) > 0:
        st.divider()
        st.subheader("🔮 今晚預測結果")
        
        # 拖牌權重演算法
        pool = []
        total_rows = len(df)
        for i in range(total_rows - 1):
            current_set = set(df.iloc[i][['n1','n2','n3','n4','n5']].values)
            matches = len(current_set.intersection(set(last_nums)))
            
            if matches >= 1:
                # 越近期的數據，權重越高 (i 越大權重越高)
                recency_bonus = (i / total_rows) + 1 
                next_issue = df.iloc[i+1][['n1','n2','n3','n4','n5']].values
                # 根據匹配數與近期性重複加入池中
                weight = int(matches * recency_bonus * 2)
                for _ in range(weight):
                    pool.extend(next_issue)
        
        if pool:
            suggestions = Counter(pool).most_common(5)
            cols = st.columns(5)
            for idx, (num, val) in enumerate(suggestions):
                cols[idx].metric(f"臆測 {idx+1}", f"{int(num):02d}", f"強度 {val}")
        
        # 加強分析：年度冷熱對比
        st.write("---")
        all_nums = df[['n1','n2','n3','n4','n5']].values.flatten()
        counts = Counter(all_nums)
        hot_nums = [f"{int(n):02d}" for n, c in counts.most_common(3)]
        cold_nums = [f"{int(n):02d}" for n, c in sorted(counts.items(), key=lambda x:x[1])[:3]]
        
        c1, c2 = st.columns(2)
        c1.success(f"🔥 全年最強勢：{', '.join(hot_nums)}")
        c2.warning(f"❄️ 全年最冷門：{', '.join(cold_nums)}")
else:
    st.error("數據庫連線失敗，請檢查 GitHub history.csv 格式。")
