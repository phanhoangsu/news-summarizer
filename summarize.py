import os
import requests
from google import genai
from google.genai import types

# Lấy các Secret
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

# Danh sách 3 chủ đề kèm yêu cầu bắt buộc lấy tin mới nhất trong 1-2 ngày qua
topics = [
    {
        "category": "TECHNOLOGY 💻",
        "query": "Latest prominent breaking news in Technology, AI, or Software Development published within the last 1-2 days."
    },
    {
        "category": "BUSINESS 📈",
        "query": "Latest prominent business news, global startups, or market trends published within the last 1-2 days."
    },
    {
        "category": "STOCK MARKET 📊",
        "query": "Latest stock market updates, major economic movements, or financial analysis published within the last 1-2 days."
    }
]

print("Đang tìm kiếm và tổng hợp 3 bản tin mới nhất từ Internet...")

for item in topics:
    category = item["category"]
    query_topic = item["query"]
    
    prompt = f"""
    You are a professional REAL-TIME NEWS RESEARCHER and WORKSHEET FILLER. 
    Search for and use REAL, RECENT news published within the last 1-2 days regarding: "{query_topic}".
    Do not use old or outdated events. Base your information strictly on the latest search results.
    Then, fill in the EXACT worksheet format based on that news. Keep answers concise, using keywords and facts only.

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

    try:
        # Bật công cụ Google Search (Grounding) để AI bắt buộc phải tìm kiếm tin thực tế trên web
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}],
                temperature=0.3, # Giảm độ sáng tạo để AI tập trung bám sát sự kiện thực tế
            )
        )
        worksheet_result = response.text.strip()
        
        # Format nội dung gửi Telegram cho từng chủ đề
        message_text = f"🚀 *{category}* *(Real-time 1-2 days)*\n\n```text\n{worksheet_result}\n```"
        
        # Gửi về Telegram
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message_text,
                "parse_mode": "Markdown"
            }
            res = requests.post(telegram_url, json=payload)
            if res.status_code == 200:
                print(f"Đã gửi thành công bản tin thực tế chủ đề: {category}")
            else:
                print(f"Lỗi gửi Telegram chủ đề {category}:", res.text)
        else:
            print("Chưa cấu hình Telegram Token hoặc Chat ID.")
            
    except Exception as e:
        print(f"Lỗi khi xử lý chủ đề {category}: {str(e)}")

print("Hoàn tất quy trình gửi 3 bản tin thời gian thực!")
