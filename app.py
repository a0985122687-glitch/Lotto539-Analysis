import streamlit as st
import pandas as pd
from collections import Counter
from datetime import datetime

# 1. 頁面隱藏式設定
st.set_page_config(page_title="539 數據臆測大師", layout="centered")
st.title("🧪 539 大數據：今晚號碼臆測模型")
st.write(f"📅 預測基準日：{datetime.now().strftime('%Y-%m-%d')} (中午時段)")
st.write("---")

# 2. 載入大數據 (history.csv)
@st.cache_data
def load_big_data():
    url = "https://raw.githubusercontent.com/a0985122687-glitch/Lotto539-Analysis/main/history.csv"
    try:
        # 讀取 CSV，並跳過格式錯誤的行
        df = pd.read_csv(url, on_bad_lines='skip')
        # 確保數字欄位正確
        for col in ['n1','n2','n3','n4','n5']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.dropna().sort_values('date')
    except:
        return pd.DataFrame()

df = load_big_data()

if not df.empty:
    sample_size = len(df)
    st.info(f"✅ 大數據庫載入成功！目前分析樣本：{sample_size} 期。")
    
    # 3. 核心邏輯：觀察前一晚開出的 5 個號碼
    st.subheader("🎯 步驟一：輸入昨晚開獎號碼")
    st.write("請輸入昨晚的 5 個號碼，系統將掃描一年份數據進行「拖牌臆測」。")
    
    # 讓使用者輸入昨晚號碼
    last_nums = st.multiselect("昨晚獎號：", range(1, 40), default=None, max_selections=5)
    
    if len(last_nums) > 0:
        # 掃描歷史：當這幾個號碼出現時，隔一期最常開什麼
        potential_pool = []
        for i in range(sample_size - 1):
            current_issue = df.iloc[i][['n1','n2','n3','n4','n5']].values
            # 如果昨晚的號碼中有任何一個出現在歷史紀錄中
            matches = set(last_nums).intersection(set(current_issue))
            if matches:
                # 權重加成：匹配越多，下一期號碼權重越高
                weight = len(matches)
                next_issue = df.iloc[i+1][['n1','n2','n3','n4','n5']].values
                for _ in range(weight):
                    potential_pool.extend(next_issue)
        
        if potential_pool:
            counts = Counter(potential_pool)
            top_suggest = counts.most_common(5)
            
            st.divider()
            st.subheader("🔮 今晚可能開出的號碼臆測")
            st.write("根據歷史拖牌權重計算，今晚推薦關注：")
            
            cols = st.columns(5)
            for idx, (num, weight) in enumerate(top_suggest):
                with cols[idx]:
                    st.metric(label=f"推利 No.{idx+1}", value=f"{int(num):02d}", delta=f"熱度 {weight}")
            
            st.warning("💡 提示：此模型建議從上方預測選 2 號，並搭配下方年度熱門選 1 號。")
        else:
            st.warning("當前數據庫中尚未發現與此組合相關的歷史規律。")

    # 4. 年度熱門區 (穩定膽碼)
    st.divider()
    st.subheader("🔥 年度大數據熱門區")
    all_nums = df[['n1','n2','n3','n4','n5']].values.flatten()
    hot_5 = [f"{int(n):02d}" for n, c in Counter(all_nums).most_common(5)]
    st.success(f"這一年最常出現的穩定號碼：{', '.join(hot_5)}")

else:
    st.error("找不到正確格式的數據。請確保 history.csv 第一行是 date,n1,n2,n3,n4,n5")
