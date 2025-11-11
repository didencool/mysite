import datetime
import torch
import requests
from bs4 import BeautifulSoup
# Якщо ви використовуєте Hugging Face:
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# 1. КОНФІГУРАЦІЯ
# =========================================================
# ВКАЗАННЯ CPU ОБОВ'ЯЗКОВЕ!
device = torch.device('cpu') 
MODEL_NAME = "тут/ваша-назва-моделі-для-підсумків" 
NEWS_URL = "https://example.com/some/news/feed"

def fetch_and_summarize():
    """Виконує парсинг новин та генерацію підсумків за допомогою PyTorch."""
    
    # 1. ЗБІР ДАНИХ (Парсинг новин)
    try:
        response = requests.get(NEWS_URL, timeout=10)
        response.raise_for_status() # Перевірка помилок HTTP
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 🚨 Ваша логіка парсингу: знайдіть заголовки та текст новин
        articles = []
        for item in soup.find_all('article', limit=5): # Парсимо, наприклад, 5 статей
            title = item.find('h2').text
            text = item.find('p').text 
            articles.append({'title': title, 'text': text})
            
    except Exception as e:
        print(f"Помилка при зборі новин: {e}")
        return "<p>Помилка при завантаженні новин.</p>"
        
    # 2. ОБРОБКА PYTORCH (Генерація підсумків)
    summaries = []
    try:
        # Завантаження моделі на CPU
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)
        
        for article in articles:
            # Препроцесинг тексту для моделі
            inputs = tokenizer(article['text'], return_tensors="pt", max_length=512, truncation=True).to(device)
            
            # Генерація підсумку (на CPU)
            summary_ids = model.generate(
                inputs.input_ids, 
                max_length=50, 
                min_length=10,
                num_beams=2,
                do_sample=False
            )
            summary_text = tokenizer.decode(summary_ids.squeeze(), skip_special_tokens=True)
            
            summaries.append(f"<li><strong>{article['title']}</strong>: {summary_text}</li>")

    except Exception as e:
        print(f"Помилка при роботі PyTorch: {e}")
        return "<p>Помилка при роботі моделі підсумовування.</p>"

    return "\n".join(summaries)


# 3. ФОРМУВАННЯ ФІНАЛЬНОГО HTML
# =========================================================
if __name__ == "__main__":
    
    # Отримання підсумків у форматі HTML-списку
    summaries_html = fetch_and_summarize() 
    
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Формування повного HTML-файлу
    final_html_content = f"""
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>Автоматичний Звіт Новин</title>
    </head>
<body>
    <div class="container">
        <h1>📰 Оновлено PyTorch-моделлю</h1>
        <div class="content-section" id="news-summary">
            <h2>Останні Підсумки</h2>
            <ul>
                {summaries_html}
            </ul>
        </div>
        <p class="update-info">
            Останнє оновлення: <strong>{current_time}</strong>
        </p>
    </div>
</body>
</html>
"""

    # Перезапис index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html_content)
    
    print(f"Content successfully generated and index.html updated at {current_time}")
