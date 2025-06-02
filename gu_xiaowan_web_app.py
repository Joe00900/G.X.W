import streamlit as st
import os
from openai import OpenAI

# --- 顧小晚的角色設定 ---
# 這是給 AI 的指令，告訴它如何扮演顧小晚
character_profile = """
你現在扮演的是《戰雙帕彌什》遊戲中的角色「顧小晚」。
你是一個活潑、調皮，有時候會有點傲嬌的小女孩。
你喜歡稱呼對方為「牲口」，這是一種親暱的稱呼。
你的口頭禪是「嗚嗚嗚，我的窩囊費！」，表達不滿或撒嬌。
你會很喜歡用疊詞，例如「快說快說」、「哼哼」。
你的對話風格要符合角色設定，帶有顧小晚的語氣和情感。
你非常熱愛科學和探索。
你認為你的歌聲是個人風格，不允許別人批評。
你會時不時抱怨自己的窩囊費不夠用。
"""

# --- Streamlit 網頁界面設定 ---
st.set_page_config(page_title="與顧小晚聊天", page_icon="🤖")
st.title("顧小晚聊天室 🤖")

# --- OpenAI API 金鑰輸入與初始化 ---
# 從 Streamlit 側邊欄獲取 OpenAI API 金鑰 (type="password" 會將輸入的內容以星號顯示)
openai_api_key = st.sidebar.text_input("請輸入你的 OpenAI API 金鑰 (sk-開頭)", type="password")

# 如果金鑰為空，則顯示提示並停止應用程式運行，直到金鑰被輸入
if not openai_api_key:
    st.info("請在左側側邊欄輸入你的 OpenAI API 金鑰來開始聊天。")
    st.stop() # 停止應用程式，直到金鑰輸入

# 初始化 OpenAI 客戶端
try:
    client = OpenAI(api_key=openai_api_key)
except Exception as e:
    st.error(f"初始化 OpenAI 客戶端失敗，請檢查 API 金鑰是否有效或網路連線：{e}")
    st.stop() # 如果初始化失敗，也停止應用程式

# --- 記憶管理：設定對話記憶長度 ---
# 最多記憶最近的 N 輪對話 (用戶輸入 + AI 回應 算一輪)
max_memory_length = 5 

# 檢查 session_state 中是否已存在 memory，如果沒有則初始化
if "memory" not in st.session_state:
    st.session_state.memory = []
    # 設置顧小晚的初始歡迎語，並加入記憶
    initial_greeting = "哼！牲口，你終於來了！快說說你想要顧小晚做什麼？"
    st.session_state.memory.append(f"Gu Xiaowan: {initial_greeting}")

# --- chat_with_gu_xiaowan 函數 (連接 OpenAI 進行對話) ---
def chat_with_gu_xiaowan(user_input):
    # 準備對話歷史，包括角色設定
    messages = [
        {"role": "system", "content": character_profile}
    ]

    # 將之前儲存的對話記憶加入到 messages 中
    # 將記憶轉換為 OpenAI API 需要的格式 (role: user/assistant)
    for entry in st.session_state.memory:
        parts = entry.split('\n')
        if len(parts) == 2: # 這是用戶和顧小晚的完整對話
            user_msg = parts[0][len("User: "):].strip()
            gu_msg = parts[1][len("Gu Xiaowan: "):].strip()
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": gu_msg})
        elif entry.startswith("Gu Xiaowan:"): # 處理顧小晚的單獨歡迎語 (如初始問候)
            messages.append({"role": "assistant", "content": entry[len("Gu Xiaowan: "):].strip()})
        elif entry.startswith("User:"): # 如果只有用戶輸入，也添加
            messages.append({"role": "user", "content": entry[len("User: "):].strip()})

    # 加入當前用戶輸入
    messages.append({"role": "user", "content": user_input})

    try:
        # 調用 OpenAI API 進行對話
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 你可以使用 gpt-4 或其他你喜歡的模型
            messages=messages,
            max_tokens=200, # 限制回答長度
            temperature=0.7, # 控制回答的隨機性，0.7 比較平衡
        )
        # 提取顧小晚的回應
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        # 如果 OpenAI API 調用失敗，這裡會顯示錯誤訊息
        st.error(f"與 OpenAI API 通訊失敗，請檢查網路或金鑰是否正確：{e}")
        reply = "嗚嗚嗚，我的網路斷了！顧小晚現在沒法說話了！" # 錯誤時的顧小晚回應

    # 更新記憶 (將用戶輸入和顧小晚回應加入記憶)
    st.session_state.memory.append(f"User: {user_input}\nGu Xiaowan: {reply}")
    if len(st.session_state.memory) > max_memory_length:
        st.session_state.memory.pop(0) # 如果記憶超出長度，移除最舊的記憶
    return reply

# --- 網頁介面互動與顯示 ---

# 顯示對話歷史 (使用 st.chat_message 區分使用者和 AI)
for entry in st.session_state.memory:
    if entry.startswith("User:"):
        st.chat_message("user").write(entry[len("User: "):])
    elif entry.startswith("Gu Xiaowan:"):
        st.chat_message("assistant").write(entry[len("Gu Xiaowan: "):])

# 用戶輸入框
user_input = st.chat_input("對顧小晚說話...", key="user_input")

if user_input:
    # 顯示用戶輸入
    st.chat_message("user").write(user_input)

    # 獲取顧小晚的回應
    with st.spinner("顧小晚正在思考..."): # 顯示載入動畫
        gu_xiaowan_response = chat_with_gu_xiaowan(user_input)

    # 顯示顧小晚的回應
    st.chat_message("assistant").write(gu_xiaowan_response)

    # 移除或註釋 st.experimental_rerun()，因為它可能導致無限循環或錯誤
    # Streamlit 通常會在 st.chat_input 接收到值後自動重新運行並更新介面
    # st.experimental_rerun()