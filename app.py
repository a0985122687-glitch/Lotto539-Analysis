import streamlit as st
import pandas as pd
from collections import Counter

# 1. 頁面設定 (維持簡潔模板)
st.set_page_config(page_title="539 數據臆測大師", layout="centered")
st.title("🧪 539 大數據：今晚號碼臆測模型")

# 2. 核心讀取邏輯 (修正樣本數不夠的問題)
@st.cache_data
def load_and_clean_data():
    url = "https://raw.githubusercontent.com/a0985122687-glitch/Lotto539-Analysis/main/history.csv"
    try:
        # 針對您的檔案格式進行特殊讀取 (處理空格或逗號)
        df = pd.read_csv(url, sep=r'\s+|,', engine='python', names=['id', 'date', 'n1', 'n2', 'n3', 'n4', 'n5'], skiprows=1)
        # 強制轉換數字格式
        for col in ['id', 'n1', 'n2', 'n3', 'n4', 'n5']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.dropna().sort_values('id')
    except:
        return pd.DataFrame()

df = load_and_clean_data()

if not df.empty:
    # 顯示樣本數 (這就是您要核對的地方)
    st.info(f"✅ 大數據分析樣本已載入：{len(df)} 期")
    
    st.subheader("🎯 昨晚開獎基準 (對期別)")
    # 讓您選期別，App 會自動帶出號碼，保證精準
    selected_id = st.selectbox("請確認昨晚期別：", df['id'].unique()[::-1])
    target = df[df['id'] == selected_id].iloc[0]
    
    # 核對顯示
    current_nums = [int(target['n1']), int(target['n2']), int(target['n3']), int(target['n4']), int(target['n5'])]
    st.success(f"📅 期別：{int(target['id'])} | 獎號：{', '.join([f'{n:02d}' for n in current_nums])}")

    st.divider()
    
    # 3. 臆測結果呈現 (延續您要求的模板)
    st.subheader(f"🔮 根據期別 {int(target['id'])} 之今晚臆測")
    pool = []
    # 掃描歷史大數據
    df_list = df.values.tolist()
    for i in range(len(df_list) - 1):
        # 取得歷史中該期的 5 個號碼
        hist_nums = set(df_list[i][2:7])
        matches = len(hist_nums.intersection(set(current_nums)))
        if matches >= 1:
            # 抓取下一期的號碼
            next_nums = df_list[i+1][2:7]
            # 權重補強
            for _ in range(matches * 2):
                pool.extend(next_nums)
    
    if pool:
        # 找出強度最高的前 5 名
        suggestions = Counter(pool).most_common(5)
        cols = st.columns(5)
        for idx, (num, val) in enumerate(suggestions):
            with cols[idx]:
                st.metric(label=f"建議 {idx+1}", value=f"{int(num):02d}", delta=f"強度 {val}")
    else:
        st.warning("數據庫規律不足，請增加資料。")

else:
    st.error("請確保 history.csv 第一行是 id,date,n1,n2,n3,n4,n5 且欄位正確。")
