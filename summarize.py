import os
import time
import requests
from google import genai
from google.genai import types

# Lấy các Secret từ môi trường GitHub Actions
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

print("Đang bắt đầu quá trình tìm kiếm và tổng hợp 3 bản tin thời gian thực...")

# Gộp yêu cầu 3 chủ đề vào 1 prompt duy nhất để chỉ gọi API 1 lần
prompt = """
You are a professional REAL-TIME NEWS RESEARCHER and WORKSHEET FILLER. 
Search for and use REAL, RECENT news published within the last 1-2 days regarding these 3 topics:
1. TECHNOLOGY 💻: Latest prominent breaking news in Technology, AI, or Software Development.
2. BUSINESS 📈: Latest prominent business news, global startups, or market trends.
3. STOCK MARKET 📊: Latest stock market updates, major economic movements, or financial analysis.

Do not use old or outdated events. Base your information strictly on the latest search results.
For EACH of the 3 topics above, fill in the EXACT worksheet format provided below. Keep answers concise, using keywords and facts only.

Use this EXACT format for each topic (bắt buộc phải giữ đúng định dạng phân tách này):

=== TOPIC: [Tên chủ đề] ===
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
    # Gọi API 1 lần duy nhất có kèm theo Google Search Grounding
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[{"google_search": {}}],
            temperature=0.3,
        )
    )
    
    worksheet_result = response.text.strip()
    
    # Tách kết quả thành các phần riêng biệt dựa trên thẻ phân tách "=== TOPIC:"
    parts = worksheet_result.split("=== TOPIC:")
    
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        for part in parts:
            if not part.strip():
                continue
            
            sub_content = "=== TOPIC:" + part.strip()
            message_text = f"🚀 *BẢN TIN ĐIỂM TIN HÀNG NGÀY*\n\n```text\n{sub_content}\n```"
            
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message_text,
                "parse_mode": "Markdown"
            }
            
            res = requests.post(telegram_url, json=payload)
            if res.status_code == 200:
                print("Đã gửi thành công một phần bản tin về Telegram!")
            else:
                print("Lỗi gửi Telegram:", res.text)
                
            # Nghỉ 3 giây giữa các tin nhắn để tránh bị Telegram tính là spam
            time.sleep(3)
            
        print("Đã gửi thành công toàn bộ các phần bản tin về Telegram!")
    else:
        print("Chưa cấu hình Telegram Token hoặc Chat ID.")

except Exception as e:
    print(f"Lỗi khi xử lý tổng hợp bản tin: {str(e)}")

print("Hoàn tất toàn bộ quy trình gửi bản tin điểm tin!")
