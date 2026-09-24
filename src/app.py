"""连接 DeepSeek 官方 API。"""

import os

from openai import OpenAI

BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-v4-pro"

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url=BASE_URL)


def chat(messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    reply = chat([{"role": "user", "content": "你是谁?"}])
    print("模型回复：", reply)
