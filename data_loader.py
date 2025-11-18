import feedparser
import requests
from bs4 import BeautifulSoup
from typing import List, Dict

# --- ДОДАТКОВА ФУНКЦІЯ: Скрейпінг повного тексту ---
def fetch_full_text(url: str) -> str:
    """Намагається отримати повний текст статті за посиланням."""
    try:
        response = requests.get(url, timeout=10)
        # Встановлюємо правильне кодування, якщо це можливо
        response.encoding = response.apparent_encoding
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Загальний підхід: шукаємо теги, які часто містять основний контент
        paragraphs = soup.find_all('p')
        
        # Об'єднуємо перші 10 абзаців як основний текст
        full_text = '\n'.join([p.get_text() for p in paragraphs[:10]])
        
        # Обмежимо текст, оскільки моделі мають обмеження за токенами (до 10000 символів)
        return full_text[:10000]
    
    except Exception as e:
        return f"[Помилка скрейпінгу: {e}]"
# --- КІНЕЦЬ ДОДАТКОВОЇ ФУНКЦІЇ ---


def load_sources(file_path: str) -> List[str]:
    """Завантажує URL-адреси RSS-стрічок із зазначеного файлу."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sources = [line.strip() for line in f if line.strip()]
        return sources
    except FileNotFoundError:
        print(f"Помилка: Файл джерел не знайдено за шляхом: {file_path}")
        return []

def fetch_news(rss_sources: List[str], limit_per_source: int) -> List[Dict]:
    """Збирає заголовки та повний текст новин."""
    collected_articles = []
    
    for url in rss_sources:
        try:
            feed = feedparser.parse(url)
            print(f"Збір новин з: {url[:60]}...")
            
            for entry in feed.entries[:limit_per_source]: 
                article_link = entry.get('link', 'N/A')
                
                # --- ВИКЛИК НОВОЇ ФУНКЦІЇ ---
                full_content = fetch_full_text(article_link) 
                
                article = {
                    'title': entry.get('title', 'N/A'),
                    'link': article_link,
                    'source': url,
                    'content': full_content # <-- ТЕПЕР МИ МАЄМО ПОВНИЙ ТЕКСТ
                }
                collected_articles.append(article)
        
        except Exception as e:
            print(f"Помилка при зборі новин з {url}: {e}")
            
    print(f"Зібрано {len(collected_articles)} статей загалом.")
    return collected_articles

