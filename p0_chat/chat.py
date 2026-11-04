import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 这个列表就是"记忆"。它只存在于你的程序里，模型那边什么都没有。
messages = [
    {"role": "system", "content": "你是一个简洁的助手，回答不超过三句话。"}
]

total_tokens = 0

print("输入 q 退出\n")

while True:
    user_input = input("你：")
    if user_input.strip().lower() == "q":
        break

    messages.append({"role": "user", "content": user_input})
    # 保留 system + 最近 10 轮，超出的丢掉
    MAX_ROUNDS = 10
    if len(messages) > 1 + MAX_ROUNDS * 2:
        messages = [messages[0]] + messages[-(MAX_ROUNDS * 2):]
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
    except Exception as e:
        print("出错了：", e)
        messages.pop()
        continue

    answer = resp.choices[0].message.content
    print("AI：", answer, "\n")

    messages.append({"role": "assistant", "content": answer})
    total_tokens += resp.usage.total_tokens

print(f"\n本次共消耗 {total_tokens} token")
