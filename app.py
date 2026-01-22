import streamlit as st
import pandas as pd
from collections import Counter

# 1. 頁面設定
st.set_page_config(page_title="539 大數據拖牌建模", layout="wide")
st.title("🧪 539 大數據規律分析 (純數據版)")

# 2. 載入歷史檔案
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/a0985122687-glitch/Lotto539-Analysis/main/history.csv"
    try:
        df = pd.read_csv(url)
        # 轉換日期格式並確保數字為整數
        df['date'] = pd.to_datetime(df['date']).dt.date
        for col in ['n1','n2','n3','n4','n5']:
            df[col] = df[col].astype(int)
        # 按日期排序，最新的在上面
        df = df.sort_values('date', ascending=False)
        return df
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.success(f"📈 大數據庫已載入！目前共累積：{len(df)} 期數據。")

    # --- 區塊一：歷史獎號表格 (方便觀察) ---
    st.header("📋 歷史開獎實際號碼總覽")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # --- 區塊二：拖牌規律分析 ---
    st.divider()
    st.header("🔍 拖牌規律分析")
    st.write("概念：當某個號碼開出後，下一期最常跟著開出什麼？")
    
    target_num = st.selectbox("請選擇一個觀測號碼：", range(1, 40))
    
    # 邏輯計算：找出選定號碼的下一期號碼 (需按日期順序計算)
    df_sorted = df.sort_values('date') # 改回正序計算拖牌
    next_issue_nums = []
    for i in range(len(df_sorted) - 1):
        current_row = df_sorted.iloc[i][['n1','n2','n3','n4','n5']].values
        if target_num in current_row:
            next_row = df_sorted.iloc[i+1][['n1','n2','n3','n4','n5']].values
            next_issue_nums.extend(next_row)
            
    if next_issue_nums:
        next_counts = Counter(next_issue_nums)
        top_5 = next_counts.most_common(5)
        
        st.subheader(f"當 {target_num:02d} 開出後，下一期歷史統計最常出現：")
        cols = st.columns(5)
        for idx, (num, count) in enumerate(top_5):
            cols[idx].metric(f"熱門 No.{idx+1}", f"{num:02d}", f"出現 {count} 次")
    else:
        st.info("⚠️ 目前數據量較少（僅 2 期無法計算隔期拖牌），請繼續增加歷史數據至 history.csv 以啟動分析。")

    # --- 區塊三：數據加強建議 ---
    st.divider()
    st.subheader("💡 下一步建議")
    if len(df) < 50:
        st.warning("當前數據量不足 50 期，分析結果僅供參考。建議至少匯入近一年的數據。")
    st.write("您可以手動更新 GitHub 上的 `history.csv`，只要增加一行數據，App 就會自動更新分析結果。")

else:
    st.error("找不到 history.csv 或格式錯誤。請確保檔案內容包含 date, n1, n2, n3, n4, n5 欄位。")
