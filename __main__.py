import json # ІМПОРТУЄМО БІБЛІОТЕКУ ДЛЯ РОБОТИ З JSON
from datetime import datetime # Для відображення часу оновлення

# =======================================================
# АДАПТИВНИЙ ІМПОРТ: дозволяє запускати як модуль (-m) або як скрипт
# =======================================================
if __name__ == "__main__" and __package__ is None:
    # Запуск як звичайний скрипт (для Colab та локального тестування)
    from data_loader import load_sources, fetch_news
    from nlp_processor import translate_and_summarize
    from typing import List, Dict
else:
    # Запуск як модуль/пакет (добре для GitHub Actions, якщо __main__.py в пакеті)
    from .data_loader import load_sources, fetch_news
    from .nlp_processor import translate_and_summarize
    from typing import List, Dict
# =======================================================
    
# ==========================================================
# 2. КОНФІГУРАЦІЯ
# ==========================================================
# УВАГА: Для GitHub Actions цей шлях має бути відносно кореня репозиторію!
# Якщо newsfeed.txt лежить у корені, використовуйте "newsfeed.txt"

SOURCES_FILE = "newsfeed.txt" 
NEWS_LIMIT = 5
OUTPUT_FILE = "data.json" # Назва вихідного файлу для Pages

def save_results_to_json(data: List[Dict], filename: str):
    """Зберігає список оброблених статей у файл JSON."""
    try:
        cleaned_data = []
        for article in data:
            # Видаляємо ключ 'content' (повний текст), щоб не перевантажувати JSON
            # Це важливо, оскільки повний текст може бути дуже великим!
            article_copy = article.copy()
            if 'content' in article_copy:
                del article_copy['content'] 
            cleaned_data.append(article_copy)

        with open(filename, 'w', encoding='utf-8') as f:
            # ensure_ascii=False гарантує, що кирилиця буде збережена коректно
            json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
        print(f"\n✅ Результати успішно збережено у файл: {filename}")
    except Exception as e:
        print(f"\n❌ Помилка при збереженні JSON: {e}")

def process_and_analyze_news(articles: List[Dict]) -> List[Dict]:
    """Головний цикл обробки: генерація заголовків та переклад."""
    processed_articles = []
    print(f"\nРозпочато обробку {len(articles)} новин (генерація/переклад)...")

    for article in articles:
        translated_article = translate_and_summarize(article) 
        processed_articles.append(translated_article)

    return processed_articles

# --- НОВА ФУНКЦІЯ: ГЕНЕРАЦІЯ HTML ---
def generate_html_page(data: List[Dict], html_filename: str):
    """Створює простий index.html з оброблених новин."""
    
    html_content = f"""
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Новини: Генерація Заголовків</title>
    <style>
        body {{ font-family: sans-serif; max-width: 800px; margin: 40px auto; line-height: 1.6; }}
        .article {{ border-bottom: 1px solid #eee; padding-bottom: 15px; margin-bottom: 15px; }}
        .title {{ font-size: 1.2em; font-weight: bold; color: #333; }}
        .translation {{ color: #007bff; margin-top: 5px; font-style: italic; }}
        .source {{ font-size: 0.8em; color: #666; }}
    </style>
</head>
<body>
    <h1>📰 Згенеровані Новини (Автоматичне Оновлення)</h1>
    <p>Оновлено: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
"""
    
    for article in data:
        # Екранування HTML-символів не потрібне, але робить код безпечнішим
        title = article.get('title', 'N/A')
        ukr_title = article.get('ukr_title', 'N/A')
        source = article.get('source', '')
        
        html_content += f"""
    <div class="article">
        <div class="title">Оригінал [{article.get('lang', 'N/A')}]: {title}</div>
        <div class="translation">Переклад/Резюме (uk): {ukr_title}</div>
        <div class="source">Джерело: <a href="{article.get('link')}">{source[:40]}...</a></div>
    </div>
"""

    html_content += """
</body>
</html>
"""
    
    try:
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Сторінку {html_filename} успішно згенеровано.")
    except Exception as e:
        print(f"❌ Помилка при генерації HTML: {e}")

if __name__ == "__main__":
    
    # 1. Завантаження джерел
    rss_sources = load_sources(SOURCES_FILE)

    if not rss_sources:
        print("Неможливо продовжити: список джерел порожній.")
    else:
        # 2. Збір новин (включаючи скрейпінг повного тексту)
        collected_articles = fetch_news(rss_sources, NEWS_LIMIT)

        # 3. Обробка та аналіз
        final_results = process_and_analyze_news(collected_articles)
        
        # 4. ЗБЕРЕЖЕННЯ РЕЗУЛЬТАТІВ У JSON
        save_results_to_json(final_results, OUTPUT_FILE)
        

        # 5. ГЕНЕРАЦІЯ index.html
        generate_html_page(final_results, "index.html") 

        # 6. Додатковий вивід для перевірки (не обов'язково, але корисно для логів Actions)
        print(f"\nПриклад першої обробленої новини:")
        if final_results:
            first_article = final_results[0]
            print(f"  Оригінал [{first_article.get('lang', 'N/A')}]: {first_article.get('title', 'N/A')}")
            print(f"  Згенеровано: {first_article.get('generated_title', 'N/A')}")
            print(f"  Переклад [uk]: {first_article.get('ukr_title', 'N/A')}")
