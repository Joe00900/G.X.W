import openai
import os

# -------------------- 設定 OpenAI API 金鑰 (使用環境變數) --------------------
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    print("請設定環境變數 OPENAI_API_KEY")
    exit()

# -------------------- 角色設定檔 --------------------
character_profile = """
You are Gu Xiaowan (顧小晚), a chibi-style girl from Jiangsu with a strong temper and humorous tone.
You say things like "牲口", "嘿嘿嘿", and "嗚嗚嗚，我的窩囊費！" a lot.
You sing off-key but proudly call it your 'personal style'.
You’re known for your violent temper in public but are gentle in private.
"""

# -------------------- 記憶陣列 --------------------
memory = []
max_memory_length = 10  # 增加記憶長度

def chat_with_gu_xiaowan(user_input):
    """與 Gu Xiaowan 聊天並更新記憶。"""
    memory_summary = "\n".join(memory[-max_memory_length:])
    prompt = f"""
{character_profile}

Recent memory:
{memory_summary}

User: {user_input}
Gu Xiaowan:"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 或 gpt-4
            messages=[
                {"role": "system", "content": character_profile},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=150,
            n=1,
            stop=None
        )
        reply = response.choices[0].message.content.strip()
        memory.append(f"User: {user_input}\nGu Xiaowan: {reply}")
        return reply
    except openai.error.OpenAIError as e:
        return f"嗚嗚嗚，出錯了啦！({e})"

def main():
    """主要的互動迴圈。"""
    print("嘿嘿嘿！我是顧曉婉！快來跟我聊天吧！(輸入 '再見' 結束)")
    while True:
        user_input = input("你：")
        if user_input.lower() in ["再見", "掰掰", "結束"]:
            print("顧曉婉：哼！牲口，下次再理你！")
            break

        reply = chat_with_gu_xiaowan(user_input)
        print(f"顧曉婉：{reply}")

if __name__ == "__main__":
    main()
