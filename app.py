import streamlit as st
import pandas as pd
from collections import Counter
from datetime import datetime

# 1. 頁面設定
st.set_page_config(page_title="539 大數據建模大師", layout="centered")
st.title("🍀 539 大數據：今晚臆測強化版")
st.write(f"📅 當前分析時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}")

# 2. 強化版數據讀取邏輯
@st.cache_data(ttl=3600)
def load_and_fix_data():
    url = "https://raw.githubusercontent.com/a0985122687-glitch/Lotto539-Analysis/main/history.csv"
    try:
        # 使用正規表達式處理空格或逗號分隔，並自動跳過標頭雜質
        df = pd.read_csv(url, sep=r'\s+|,', engine='python', on_bad_lines='skip')
        # 強制對齊欄位
        if len(df.columns) >= 7:
            df = df.iloc[:, :7]
            df.columns = ['id', 'date', 'n1', 'n2', 'n3', 'n4', 'n5']
        
        # 轉換數字格式並清洗
        for col in ['id', 'n1', 'n2', 'n3', 'n4', 'n5']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.dropna().sort_values('id', ascending=True)
    except:
        return pd.DataFrame()

df = load_and_fix_data()

if not df.empty:
    # 顯示樣本數核對
    st.info(f"📊 大數據庫已連線：共累積 {len(df)} 期樣本")
    
    # 3. 自動對齊最新期別
    st.subheader("🎯 昨晚開獎基準核對")
    latest_issue = df.iloc[-1]
    
    # 下拉選單預設選中最新一期
    selected_id = st.selectbox("確認基準期別：", df['id'].unique()[::-1], index=0)
    target = df[df['id'] == selected_id].iloc[0]
    
    # 顯示核對號碼
    ref_nums = [int(target['n1']), int(target['n2']), int(target['n3']), int(target['n4']), int(target['n5'])]
    st.success(f"✅ 已選定期別：{int(target['id'])} | 獎號：{', '.join([f'{n:02d}' for n in ref_nums])}")

    # 4. 強化臆測建模 (拖牌權重演算法)
    st.divider()
    st.subheader("🔮 今晚 (01/23) 號碼臆測建議")
    
    pool = []
    df_list = df.values.tolist()
    for i in range(len(df_list) - 1):
        # 提取該行號碼並與基準號碼比對
        hist_nums = set(df_list[i][2:7])
        matches = len(hist_nums.intersection(set(ref_nums)))
        
        if matches >= 1:
            # 取得「下一期」號碼
            next_nums = df_list[i+1][2:7]
            # 權重優化：匹配號碼越多，該規律權重越高
            weight = matches * 3
            for _ in range(weight):
                pool.extend(next_nums)
    
    if pool:
        # 計算前 5 名
        top_5 = Counter(pool).most_common(5)
        
        # 以精美的卡片呈現
        cols = st.columns(5)
        for idx, (num, val) in enumerate(top_5):
            with cols[idx]:
                st.metric(label=f"建議 {idx+1}", value=f"{int(num):02d}", delta=f"強度 {val}")
        
        st.write("---")
        st.caption("💡 強度說明：代表在歷史 300 多期中，當基準號碼出現後，該號碼在下一期跟著出現的權重總和。")
    else:
        st.warning("目前的數據量尚不足以對此特定組合產生臆測，建議繼續增加歷史數據。")

else:
    st.error("⚠️ 數據讀取異常。請檢查 GitHub 上的 history.csv 格式是否為 id,date,n1,n2,n3,n4,n5")

# 5. 快速操作手冊
with st.expander("🛠️ 每日強化操作手冊"):
    st.write("""
    1. **每日晚上 8:40**：至 GitHub 更新當晚最新號碼到 `history.csv` 最後一行。
    2. **每日中午**：打開此 App，確認基準期別已自動更新為昨晚。
    3. **查看建議**：系統會根據 2025 年一整年的數據，自動計算出今晚最值得關注的數字。
    """)
