import time
import os
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from google import genai

st.title("Study with Fish .・")
st.caption("おさかなといっしょに勉強しよう！")


st.markdown("""
 <style>
    /* メインの背景 */
    .stApp {
    background-color: #7fe3ff;
     color: #ffffff;
     }  

 
     /*ヘッダー透明・右上のボタン削除 */
     header {
     background-color: transparent !important;
     }
     [data-testid="stAppDeployButton"], [data-testid="stMainMenu"] {
     display: none !important;
     }
 
     /* サイドバーの背景 */
     [data-testid="stSidebar"] {
     background-color: #00B4E6;
     border-right: 1px solid #1a2e4c;
     }

    /*サイドバー内の文字・白*/
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h2 {
     color: #ffffff !important;
    }
     /*ボタンのスタイル*/
      .stButton>button {
     background-color: #33D3FF;
        color: #ffffff;
     border-radius: 8px;
     font-weight: bold;
     }
    /* ボタンホバー時 */
     .stButton>button:hover {
       background-color: #00B5FF !important;
     border-color: #33D3FF !important;
     }
     </style>
""", unsafe_allow_html=True)



#APIキーの設定
api_key = st.text_input("Gemini API Keyを入力してください", type="password")

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        MODEL_NAME = "gemini-3.5-flash-lite"
    except Exception as e:
         st.error(f"APIクライアントの初期化に失敗しました: {e}")
         client = None
else:
    st.warning("魚と会話するには、APIキーを入力してください。")
    client = None


def load_data():
    if not os.path.exists("data.csv"):
        df = pd.DataFrame(columns=["日付", "時間", "魚"])
        df.to_csv("data.csv", index=False)
        return df
    df = pd.read_csv("data.csv")

    valid_cols = [c for c in ["日付", "時間", "魚"] if c in df.columns]
    return df[valid_cols]

df = load_data()

if "total_minutes" not in st.session_state:
    st.session_state.total_minutes = 0
if "fish_message" not in st.session_state:
    st.session_state.fish_message = "いっしょに勉強をはじめよう！"
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "timer_paused" not in st.session_state:
    st.session_state.timer_paused = False
if "timer_start_time" not in st.session_state:
    st.session_state.timer_start_time = None
if "accumulated_seconds" not in st.session_state:
    st.session_state.accumulated_seconds = 0

# サイドページ
st.sidebar.header("⚙️ 設定")

fish_option = st.sidebar.selectbox(
    "いっしょに勉強する魚を選んでね",
    ["金魚", "鯖"]
)

study_topic = st.sidebar.text_input("今日勉強する内容", placeholder="例：漢字練習")

# メイン画面
# 魚の画像エリア
col1, col2, col3 = st.columns([1, 2, 1])
with col2: 

     if fish_option == "金魚":
         st.image("img/kingyo.gif", use_container_width=True)
     elif fish_option == "鯖":
        st.image("img/saba.gif", use_container_width=True)

     # レベル表示
     if st.session_state.total_minutes < 1:
         level = 1
     elif st.session_state.total_minutes < 10:
         level = 2
     elif st.session_state.total_minutes < 60:
        level = 3
     else:
        level = 4
     st.markdown(f"<h4 style='text-align: center;'>Level {level}</h4>", unsafe_allow_html=True)

# 魚からのメッセージを表示
st.chat_message("assistant", avatar="🐠").write(st.session_state.fish_message)

st.write("---")

# タイマー表示
timer_placeholder = st.empty()

# 現在の経過時間を計算
current_seconds = st.session_state.accumulated_seconds
if st.session_state.timer_running and not st.session_state.timer_paused and st.session_state.timer_start_time is not None:
    current_seconds += int(time.time() - st.session_state.timer_start_time)

hours, remainder = divmod(current_seconds, 3600)
mins, secs = divmod(remainder, 60)
timer_placeholder.markdown(f"<h1 style='text-align: center;'>{hours}:{mins:02d}:{secs:02d}</h1>", unsafe_allow_html=True)

# 自動更新
if st.session_state.timer_running and not st.session_state.timer_paused:
    st_autorefresh(interval=1000, key="timer_refresh")

# コントロールボタン配置
btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
    if st.button("❌ 削除", use_container_width=True):
        st.session_state.timer_running = False
        st.session_state.timer_paused = False
        st.session_state.timer_start_time = None
        st.session_state.accumulated_seconds = 0
        st.session_state.fish_message = "タイマーをリセットしたよ。いつでも再開してね！"
        st.rerun()

with btn_col2:
    # ▶️と⏸️が切り替え
    if st.session_state.timer_running and not st.session_state.timer_paused:
        if st.button("⏸️ 一時停止", use_container_width=True):
            st.session_state.accumulated_seconds += int(time.time() - st.session_state.timer_start_time)
            st.session_state.timer_paused = True
            st.session_state.timer_start_time = None
            st.rerun()
    elif st.session_state.timer_running and st.session_state.timer_paused:
        if st.button("▶️ 再生", use_container_width=True):
            st.session_state.timer_paused = False
            st.session_state.timer_start_time = time.time()
            st.rerun()
    else:
        st.button("⏸️ 一時停止", use_container_width=True, disabled=True)

with btn_col3:
    #完了/開始ボタン＋てきすと
    start_label = "✅ 完了" if st.session_state.timer_running else "✅ 開始"
    if st.button(start_label, use_container_width=True):
        if not st.session_state.timer_running:
            # 「開始」が押されたとき
            st.session_state.timer_running = True
            st.session_state.timer_paused = False
            st.session_state.timer_start_time = time.time()
            st.session_state.accumulated_seconds = 0

            #Geminiの応援メッセージ
            if client:
                # 内容が空欄の場合のテキスト
                topic_text = study_topic if study_topic else "お勉強"
                prompt = (
                    f"あなたは勉強管理アプリのキャラクターである魚の「{fish_option}」です。"
                    f"ユーザーは今から「{topic_text}」を勉強します。ぷくぷくから始まる、かわいい2文の応援メッセージを考えてください。"
                )
                try:
                    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
                    st.session_state.fish_message = response.text
                except Exception as e:
                    # エラーが起きたら固定メッセージ
                   st.session_state.fish_message = "今日も一緒にがんばろう！"

            st.rerun()
        else:
            # 「完了」が押されたとき（データを保存して終了）
            st.session_state.timer_running = False
            session_seconds = st.session_state.accumulated_seconds
            if st.session_state.timer_start_time is not None:
                session_seconds += int(time.time() - st.session_state.timer_start_time)

            earned_minutes = session_seconds // 60
            if earned_minutes > 0:
                st.session_state.total_minutes += earned_minutes
                new_data = pd.DataFrame([{
                    "日付": pd.Timestamp.now().strftime("%Y-%m-%d"),
                    "時間": f"{earned_minutes}分",
                    "魚": fish_option
                }])
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_csv("data.csv", index=False)
                st.session_state.fish_message = f"お疲れ様！{earned_minutes}分勉強した記録を保存したよ！"
            else:
                st.session_state.fish_message = "1分未満の勉強は記録されなかったよ。次はもっと長く頑張ろう！"

            st.session_state.accumulated_seconds = 0
            st.session_state.timer_start_time = None
            st.session_state.timer_paused = False
            st.rerun()


#これまでの記録
st.write("---")
st.subheader("記録")
st.dataframe(df, use_container_width=True)
