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

# Danh sách nguồn RSS trực tiếp từ Reuters
rss_topics = [
    {
        "category": "TECHNOLOGY 💻",
        "url": "https://www.reutersagency.com/feed/?best-topics=tech&post_type=best"
    },
    {
        "category": "BUSINESS 📈",
        "url": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best"
    },
    {
        "category": "STOCK MARKET 📊",
        "url": "https://www.reutersagency.com/feed/?best-topics=markets&post_type=best"
    }
]

print("Đang lấy tin tức thời gian thực từ Reuters RSS...")

def fetch_news_from_rss(rss_url):
    try:
        # Thêm User-Agent để tránh bị Reuters chặn yêu cầu kết nối
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(rss_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall('.//item')[:3] # Lấy 3 bài mới nhất từ Reuters
            news_texts = []
            for item in items:
                title = item.find('title').text if item.find('title') is not None else ""
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                description = item.find('description').text if item.find('description') is not None else ""
                # Làm sạch thẻ HTML trong description nếu có
                clean_desc = "".join(ET.fromstring(f"<root>{description}</root>").itertext()) if description else ""
                news_texts.append(f"- Tiêu đề: {title}\n  Thời gian: {pub_date}\n  Tóm tắt: {clean_desc[:200]}...")
            return "\n\n".join(news_texts)
    except Exception as e:
        print(f"Lỗi đọc RSS Reuters: {e}")
    return "Không thể lấy dữ liệu từ Reuters."

if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    for item in rss_topics:
        category = item["category"]
        raw_news = fetch_news_from_rss(item["url"])
        
        print(f"Đang xử lý chủ đề từ Reuters: {category}...")
        
        prompt = f"""
        You are a professional WORKSHEET FILLER. 
        Based on the following recent news items from Reuters, choose the most prominent one and fill in the EXACT worksheet format. Keep answers concise, using keywords and facts only.

        Reuters News Data:
        {raw_news}

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
            # Gọi Gemini xử lý văn bản thuần túy, không dùng tool search nên hoàn toàn mượt mà, không dính lỗi 429
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                )
            )
            
            worksheet_result = response.text.strip()
            message_text = f"🚀 *{category}* *(Nguồn: Reuters)*\n\n```text\n{worksheet_result}\n```"
            
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message_text,
                "parse_mode": "Markdown"
            }
            
            res = requests.post(telegram_url, json=payload)
            if res.status_code == 200:
                print(f"Đã gửi thành công bản tin Reuters chủ đề {category} về Telegram!")
            else:
                print(f"Lỗi gửi Telegram chủ đề {category}:", res.text)
                
            # Nghỉ 5 giây giữa các tin nhắn
            time.sleep(5)
            
        except Exception as e:
            print(f"Lỗi xử lý Gemini cho chủ đề {category}: {str(e)}")
            
    print("Hoàn tất toàn bộ quy trình gửi bản tin Reuters!")
else:
    print("Chưa cấu hình Telegram Token hoặc Chat ID.")





