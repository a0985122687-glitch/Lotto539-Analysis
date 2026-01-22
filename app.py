import streamlit as st
import pandas as pd
from collections import Counter

# 1. 頁面設定
st.set_page_config(page_title="539 大數據預測模型", layout="centered")
st.title("🧪 539 大數據建模規律分析")
st.write("---")

# 2. 載入 GitHub 上的歷史大數據 (history.csv)
@st.cache_data
def load_year_data():
    # 讀取你的 GitHub 原始檔案地址
    url = "https://raw.githubusercontent.com/a0985122687-glitch/Lotto539-Analysis/main/history.csv"
    try:
        df = pd.read_csv(url)
        # 確保數字格式正確
        for col in ['n1','n2','n3','n4','n5']:
            df[col] = df[col].astype(int)
        # 依日期排序
        return df.sort_values('date')
    except:
        return pd.DataFrame()

df = load_year_data()

if not df.empty:
    total_records = len(df)
    st.info(f"📊 已成功匯入大數據庫，目前累積樣本：{total_records} 期。")
    
    # --- 核心邏輯：拖牌連動分析 ---
    st.header("🔍 拖牌規律建模")
    st.write("概念：分析歷史上當「觀測號碼」出現後，下一期緊接著開出的號碼頻率。")

    # 讓使用者選擇昨晚開出的號碼作為觀測點
    target = st.selectbox("🎯 請選擇昨晚開出的其中一個號碼：", range(1, 40), index=0)
    
    # 計算拖牌規律
    next_nums = []
    for i in range(total_records - 1):
        # 如果這一期包含觀測號碼
        if target in df.iloc[i][['n1','n2','n3','n4','n5']].values:
            # 紀錄下一期的所有號碼
            following = df.iloc[i+1][['n1','n2','n3','n4','n5']].values
            next_nums.extend(following)

    if next_nums:
        counts = Counter(next_nums)
        # 取得最常出現的前 6 名
        predictions = counts.most_common(6)
        
        st.subheader(f"💡 根據歷史數據，當 {target:02d} 開出後，下一期最推薦：")
        
        # 使用直觀的指標呈現建議號碼
        cols = st.columns(3)
        for idx, (num, count) in enumerate(predictions):
            with cols[idx % 3]:
                st.metric(label=f"建議號碼 {idx+1}", value=f"{num:02d}", delta=f"歷史連動 {count} 次")
    else:
        st.warning("⚠️ 目前數據樣本量尚不足以計算此號碼的規律，請繼續增加 history.csv 的期數。")

    # --- 區塊二：年度綜合建模建議 ---
    st.divider()
    st.header("🔮 下一階段建模建議")
    
    all_year_nums = df[['n1','n2','n3','n4','n5']].values.flatten()
    year_counts = Counter(all_year_nums)
    
    # 找出全年度最熱門的號碼 (作為穩定的膽碼參考)
    top_annual = [f"{n:02d}" for n, c in year_counts.most_common(5)]
    
    st.write(f"📊 **全年度熱門膽碼建議**（根據這 {total_records} 期統計）：")
    st.success(f"🔥 強勢候選：{', '.join(top_annual)}")
    
    st.write("---")
    st.caption("數據驅動分析，僅供參考，請理性投注。您可以隨時在 GitHub 更新 history.csv 以優化模型準確度。")

else:
    st.error("找不到數據庫，請檢查 GitHub 上的 history.csv 內容。")
