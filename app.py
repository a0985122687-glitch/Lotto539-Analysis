import streamlit as st
import pandas as pd
from collections import Counter
import plotly.express as px

st.set_page_config(page_title="539 大數據規律分析", layout="wide")
st.title("🧪 539 大數據拖牌規律建模")

# 1. 載入一整年的歷史檔案
@st.cache_data
def load_year_data():
    url = "https://raw.githubusercontent.com/a0985122687-glitch/Lotto539-Analysis/main/history.csv"
    try:
        df = pd.read_csv(url)
        # 確保數字格式正確
        for col in ['n1','n2','n3','n4','n5']:
            df[col] = df[col].astype(int)
        return df
    except:
        return pd.DataFrame()

df = load_year_data()

if not df.empty:
    st.success(f"📈 成功讀取大數據庫！當前累積期數：{len(df)} 期")
    
    # --- 區塊一：年度熱度分布 ---
    st.header("1️⃣ 年度號碼熱度總覽")
    all_nums = df[['n1','n2','n3','n4','n5']].values.flatten()
    counts = Counter(all_nums)
    stat_df = pd.DataFrame([{"號碼": i, "次數": counts.get(i, 0)} for i in range(1, 40)])
    
    fig = px.bar(stat_df, x='號碼', y='次數', color='次數', 
                 title="39 個號碼出現頻率 (次數越多越熱門)", color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

    # --- 區塊二：專業拖牌規律分析 ---
    st.divider()
    st.header("2️⃣ 拖牌規律：幾期前開了什麼，下一期會開什麼？")
    
    target_num = st.selectbox("請選擇昨晚開出的其中一個號碼：", range(1, 40))
    
    # 邏輯：找出 target_num 出現的期數，並抓取下一期的所有號碼
    next_issue_nums = []
    for i in range(len(df) - 1):
        current_row = df.iloc[i][['n1','n2','n3','n4','n5']].values
        if target_num in current_row:
            # 抓取「隔一期」的號碼
            next_row = df.iloc[i+1][['n1','n2','n3','n4','n5']].values
            next_issue_nums.extend(next_row)
            
    if next_issue_nums:
        next_counts = Counter(next_issue_nums)
        next_df = pd.DataFrame(next_counts.most_common(5), columns=['號碼', '歷史拖出次數'])
        
        st.write(f"🔍 分析結果：在歷史上，當 **{target_num:02d}** 開出後，隔一期最常開出的前 5 名：")
        cols = st.columns(5)
        for idx, row in next_df.iterrows():
            cols[idx].metric(f"Top {idx+1}", f"{int(row['號碼']):02d}", f"出現 {int(row['歷史拖出次數'])} 次")
    else:
        st.info("目前的數據庫太小，還找不出這號碼的拖牌規律。")

    # --- 區塊三：下一階段建議 ---
    st.divider()
    st.subheader("💡 建模預測建議")
    st.write("建議策略：從「年度熱門區」選 2 個，從上面「拖牌規律」選 2 個，最後搭配 1 個「長期冷門號」。")

else:
    st.error("請確認 GitHub 上的 history.csv 內容是否正確（需包含 date, n1, n2, n3, n4, n5 欄位）。")
