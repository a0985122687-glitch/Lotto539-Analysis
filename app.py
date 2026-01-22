import streamlit as st
import pandas as pd
from collections import Counter
import plotly.express as px

st.set_page_config(page_title="539 數據分析-穩定版", layout="wide")
st.title("🍀 539 數據建模分析 (穩定離線版)")

# 讀取 GitHub 上的歷史資料檔案
@st.cache_data
def load_local_data():
    try:
        # 直接讀取你 GitHub 內的 history.csv
        url = "https://raw.githubusercontent.com/a0985122687-glitch/Lotto539-Analysis/main/history.csv"
        df = pd.read_csv(url)
        return df
    except:
        return pd.DataFrame()

df = load_local_data()

if not df.empty:
    st.success(f"✅ 已載入歷史數據，最後更新日期：{df['date'].iloc[-1]}")
    
    # 統計邏輯
    # 這裡我們取最後 50 筆來分析 (假設你的 CSV 夠長)
    plot_df = df.tail(50)
    all_nums = plot_df[['n1','n2','n3','n4','n5']].values.flatten()
    counts = Counter(all_nums)
    
    # 畫圖
    stat_df = pd.DataFrame([{"號碼": i, "次數": counts.get(i, 0)} for i in range(1, 40)])
    fig = px.bar(stat_df, x='號碼', y='次數', color='次數', text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("🔮 根據前日數據之今日/明日預測")
    # 簡單分析邏輯：熱門號 + 冷門號組合
    hot = [f"{n:02d}" for n, c in Counter(all_nums).most_common(5)]
    cold = [f"{n:02d}" for n, c in sorted(counts.items(), key=lambda x:x[1])[:5]]
    
    col1, col2 = st.columns(2)
    col1.metric("建議熱門膽碼", hot[0], f"頻率: {counts.get(int(hot[0]))}")
    col2.write(f"🔥 推薦組合：{', '.join(hot)}")
    col2.write(f"❄️ 補號參考：{', '.join(cold)}")
else:
    st.error("找不到 history.csv 檔案，請先在 GitHub 建立並輸入數據。")
