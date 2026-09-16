import os
from huggingface_hub import InferenceClient

# Khởi tạo client sử dụng token từ biến môi trường của GitHub Actions
client = InferenceClient(
    provider="hf-inference",
    api_key=os.environ["HF_TOKEN"],
)

# Đoạn văn bản mẫu cần tóm tắt
text_to_summarize = (
    "The tower is 324 metres (1,063 ft) tall, about the same height as an 81-storey building, "
    "and the tallest structure in Paris. Its base is square, measuring 125 metres on each side. "
    "During its construction, the Eiffel Tower surpassed the Washington Monument to become "
    "the tallest man-made structure in the world, a title it held for 41 years."
)

# Gọi model tóm tắt
result = client.summarization(
    text_to_summarize,
    model="Sachin21112004/distilbart-news-summarizer"
)

print("Kết quả tóm tắt:")
print(result)
