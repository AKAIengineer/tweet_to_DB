import os

import requests
from dotenv import load_dotenv

load_dotenv()


def translate(text):
    api_key = os.getenv("DEEPL_API_KEY")
    text = text
    source_lang = "EN"
    target_lang = "JA"

    params = {
        "auth_key": api_key,
        "text": text,
        "source_lang": source_lang,  # 翻訳対象の言語
        "target_lang": target_lang,  # 翻訳後の言語
    }

    request = requests.post(
        "https://api-free.deepl.com/v2/translate", data=params
    )  # URIは有償版, 無償版で異なるため要注意
    result = request.json()
    text_ja = result["translations"][0]["text"]
    return text_ja


if __name__ == '__main__':
    text = input("text: ")
    translate(text)
