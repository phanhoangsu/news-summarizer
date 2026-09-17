# import os
# import time
# import requests
# from google import genai
# from google.genai import types

# # Lấy các Secret từ môi trường GitHub Actions
# TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
# GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# client = genai.Client(api_key=GEMINI_API_KEY)

# print("Đang bắt đầu quá trình tìm kiếm và tổng hợp 3 bản tin thời gian thực...")

# # Gộp yêu cầu 3 chủ đề vào 1 prompt duy nhất để chỉ gọi API 1 lần
# prompt = """
# You are a professional REAL-TIME NEWS RESEARCHER and WORKSHEET FILLER. 
# Search for and use REAL, RECENT news published within the last 1-2 days regarding these 3 topics:
# 1. TECHNOLOGY 💻: Latest prominent breaking news in Technology, AI, or Software Development.
# 2. BUSINESS 📈: Latest prominent business news, global startups, or market trends.
# 3. STOCK MARKET 📊: Latest stock market updates, major economic movements, or financial analysis.

# Do not use old or outdated events. Base your information strictly on the latest search results.
# For EACH of the 3 topics above, fill in the EXACT worksheet format provided below. Keep answers concise, using keywords and facts only.

# Use this EXACT format for each topic (bắt buộc phải giữ đúng định dạng phân tách này):

# === TOPIC: [Tên chủ đề] ===
# TOPIC:
# ...
# Where:
# ...
# When:
# ...
# Who:
# ...
# WHAT (PROBLEM):
# ...
# HOW:
# ...
# WHY:
# ...
# SUMMARY:
# ...
# ANALYZING:
# 1. How this event impacts my life:
# ...
# 2. What I should do after reading this news:
# ...
# WHY DID YOU CHOOSE THIS NEWS?
# ...
# GLOBAL AWARENESS:
# ...
# """

# try:
#     # Gọi API 1 lần duy nhất có kèm theo Google Search Grounding
#     response = client.models.generate_content(
#         model="gemini-3-flash-preview",
#         contents=prompt,
#         config=types.GenerateContentConfig(
#             tools=[{"google_search": {}}],
#             temperature=0.3,
#         )
#     )
    
#     worksheet_result = response.text.strip()
    
#     # Tách kết quả thành các phần riêng biệt dựa trên thẻ phân tách "=== TOPIC:"
#     parts = worksheet_result.split("=== TOPIC:")
    
#     if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
#         telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
#         for part in parts:
#             if not part.strip():
#                 continue
            
#             sub_content = "=== TOPIC:" + part.strip()
#             message_text = f"🚀 *BẢN TIN ĐIỂM TIN HÀNG NGÀY*\n\n```text\n{sub_content}\n```"
            
#             payload = {
#                 "chat_id": TELEGRAM_CHAT_ID,
#                 "text": message_text,
#                 "parse_mode": "Markdown"
#             }
            
#             res = requests.post(telegram_url, json=payload)
#             if res.status_code == 200:
#                 print("Đã gửi thành công một phần bản tin về Telegram!")
#             else:
#                 print("Lỗi gửi Telegram:", res.text)
                
#             # Nghỉ 3 giây giữa các tin nhắn để tránh bị Telegram tính là spam
#             time.sleep(3)
            
#         print("Đã gửi thành công toàn bộ các phần bản tin về Telegram!")
#     else:
#         print("Chưa cấu hình Telegram Token hoặc Chat ID.")

# except Exception as e:
#     print(f"Lỗi khi xử lý tổng hợp bản tin: {str(e)}")

# print("Hoàn tất toàn bộ quy trình gửi bản tin điểm tin!")





import os
import time
import requests
import xml.etree.ElementTree as ET
from google import genai
from google.genai import types

# Lấy các Secret từ môi trường GitHub Actions
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

rss_topics = [
    {
        "category": "TECHNOLOGY 💻",
        "url": "https://news.google.com/rss/search?q=technology+artificial+intelligence+breaking+news&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "category": "BUSINESS 📈",
        "url": "https://news.google.com/rss/search?q=global+business+startup+breaking+news&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "category": "STOCK MARKET 📊",
        "url": "https://news.google.com/rss/search?q=stock+market+wall+street+live+updates&hl=en-US&gl=US&ceid=US:en"
    }
]

print("Đang quét các bản tin nóng hổi mới nhất từ Google News RSS...")

def fetch_latest_news(rss_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(rss_url, headers=headers, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall('.//item')[:5]
            news_list = []
            for item in items:
                title = item.find('title').text if item.find('title') is not None else ""
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                link = item.find('link').text if item.find('link') is not None else ""
                # Lưu lại thông tin gồm cả tiêu đề, ngày tháng và link gốc
                news_list.append({"title": title, "pubDate": pub_date, "link": link})
            return news_list
    except Exception as e:
        print(f"Lỗi đọc RSS: {e}")
    return []

if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    for item in rss_topics:
        category = item["category"]
        news_items = fetch_latest_news(item["url"])
        
        if not news_items:
            print(f"Không có dữ liệu tin tức cho {category}.")
            continue
            
        # Tạo danh sách các tiêu đề kèm số thứ tự để đưa vào Prompt cho Gemini chọn
        raw_news_text = ""
        for idx, n in enumerate(news_items):
            raw_news_text += f"[{idx+1}] Title: {n['title']} | Date: {n['pubDate']}\n"
        
        print(f"Đang xử lý chủ đề: {category}...")
        
        prompt = f"""
        You are an elite REAL-TIME NEWS ANALYST. 
        Below is a numbered list of recent news headlines fetched right now. 
        CRITICAL RULES: 
        1. You MUST choose the absolute newest and most trending hot news published within the last 24 to 48 hours. DO NOT use old or outdated news.
        2. You MUST write the ENTIRE output strictly in professional ENGLISH.

        Raw News Feed:
        {raw_news_text}

        Based on the freshest news item found above, you MUST follow this EXACT output format:

        SELECTED_INDEX: [Chỉ điền số thứ tự từ 1 đến 5 của bài báo bạn chọn ở trên, ví dụ: 1]
        📌 TOPIC: [Hot event title]
        📍 Where: [Location / Country]
        ⏰ When: [Latest timestamp within 1-2 days]
        👤 Who: [Key figures / Companies involved]

        🔴 WHAT (PROBLEM):
        ...
        ⚡ HOW (Resolution / Development):
        ...
        💡 WHY (Root cause / Significance):
        ...

        📝 SUMMARY:
        ...

        📊 ANALYZING:
        1️⃣ Impact on my life: ...
        2️⃣ What I should do: ...

        🎯 WHY DID YOU CHOOSE THIS NEWS?: ...
        🌐 GLOBAL AWARENESS: ...
        """
        
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                )
            )
            
            response_text = response.text.strip()
            
            # Xử lý tách phần chỉ số được chọn và nội dung hiển thị
            selected_link = "https://news.google.com"
            worksheet_result = response_text
            
            if "SELECTED_INDEX:" in response_text:
                parts = response_text.split("SELECTED_INDEX:")
                if len(parts) > 1:
                    index_part = parts[1].strip().split("\n")[0].strip()
                    # Lọc lấy ký tự số
                    digits = "".join([c for c in index_part if c.isdigit()])
                    if digits:
                        chosen_idx = int(digits) - 1
                        if 0 <= chosen_idx < len(news_items):
                            selected_link = news_items[chosen_idx]["link"]
                    
                    # Loại bỏ dòng SELECTED_INDEX ra khỏi nội dung gửi về Telegram để giao diện không bị thừa
                    worksheet_result = "\n".join(response_text.split("\n")[1:]).strip()

            # Gói kết quả vào block code chuẩn template kèm đúng link gốc của bài báo đó
            message_text = (
                f"🔥 *HOT NEWS - {category}* 🔥\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"```text\n{worksheet_result}\n```\n"
                f"🔗 *Source Link:* [Click here to read original article]({selected_link})\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"✨ _Automated by AI System_"
            )
            
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message_text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False
            }
            
            res = requests.post(telegram_url, json=payload)
            if res.status_code == 200:
                print(f"Đã gửi thành công bản tin {category} kèm đúng link bài báo về Telegram!")
            else:
                print(f"Lỗi gửi Telegram chủ đề {category}:", res.text)
                
            time.sleep(5)
            
        except Exception as e:
            print(f"Lỗi xử lý Gemini cho chủ đề {category}: {str(e)}")
            
    print("Hoàn tất toàn bộ quy trình gửi hot news!")
else:
    print("Chưa cấu hình Telegram Token hoặc Chat ID.")
