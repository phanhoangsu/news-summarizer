import os
import requests
from google import genai

# Lấy các Secret
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Văn bản tin tức mẫu
article_text = """
The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. 
It is named after the engineer Gustave Eiffel, whose company designed and built the tower. 
Constructed from 1889 to 1889 as the entrance to the 1889 World's Fair, it was initially criticized by some of France's leading artists and intellectuals for its design, but it has become a global cultural icon of France and one of the most widely recognized structures in the world. 
The tower is 324 metres (1,063 ft) tall, about the same height as an 81-storey building. 
Its base is square, measuring 125 metres on each side. During its construction, it surpassed the Washington Monument to become the tallest man-made structure in the world, a title it held for 41 years.
"""

# Prompt định dạng theo đúng chuẩn Worksheet yêu cầu
prompt = f"""
You are a NEWS WORKSHEET FILLER. Extract the most important information from the text below and fill in the EXACT worksheet format. Keep answers short, using keywords and important facts only. Do not invent information. If missing, write "Not stated".

Text: {article_text}

Use this EXACT format:
TOPIC:
...
Where:
...
When:
...
Who:
...
WHAT (PROBLEM):
...
HOW:
...
WHY:
...
SUMMARY:
...
ANALYZING:
1. How this event impacts my life:
...
2. What I should do after reading this news:
...
WHY DID YOU CHOOSE THIS NEWS?
...
GLOBAL AWARENESS:
...
"""

print("Đang tạo Worksheet bằng Gemini AI...")
client = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)
worksheet_result = response.text.strip()

print("Kết quả Worksheet:\n", worksheet_result)

# Gửi kết quả về Telegram Bot cá nhân của bạn
if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"📋 *DAILY NEWS WORKSHEET*\n\n```text\n{worksheet_result}\n```",
        "parse_mode": "Markdown"
    }
    res = requests.post(telegram_url, json=payload)
    if res.status_code == 200:
        print("Đã gửi tin nhắn về Telegram thành công!")
    else:
        print("Lỗi khi gửi Telegram:", res.text)
else:
    print("Chưa cấu hình đầy đủ thông tin Telegram.")
