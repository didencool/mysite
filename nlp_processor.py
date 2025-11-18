from langdetect import detect
from transformers import pipeline
from typing import List, Dict

# ==========================================================
# ІНІЦІАЛІЗАЦІЯ МОДЕЛЕЙ
# ==========================================================
# device=0 - вказує використовувати GPU
try:
    # 1. Моделі для перекладу (залишаємо, оскільки новина може бути UK)
    EN_UK_TRANSLATOR = pipeline("translation", model="Helsinki-NLP/opus-mt-en-uk", device=0)
    RU_UK_TRANSLATOR = pipeline("translation", model="Helsinki-NLP/opus-mt-ru-uk", device=0)
    
    # 2. Модель для резюмування (Generates Title)
    # Використовуємо універсальну модель для резюмування
    SUMMARIZER = pipeline("summarization", model="facebook/bart-large-cnn", device=0) 

except Exception as e:
    print(f"Помилка при ініціалізації моделей: {e}")
    EN_UK_TRANSLATOR, RU_UK_TRANSLATOR, SUMMARIZER = None, None, None


def detect_language(text: str) -> str:
    """Визначає мову тексту."""
    if not text: return 'unknown'
    try: return detect(text[:200])
    except: return 'unknown'


def translate_and_summarize(article: Dict) -> Dict:
    """Визначає мову, генерує заголовок та перекладає його."""
    
    content = article.get('content', '')
    original_title = article.get('title', '')
    lang_code = detect_language(content)
    article['lang'] = lang_code
    
    # Визначаємо, який текст будемо обробляти
    text_to_process = content
    
    # --- ГЕНЕРАЦІЯ НОВОГО ЗАГОЛОВКА ---
    new_title = original_title 
    
    if SUMMARIZER and len(text_to_process) > 200 and lang_code in ['en']: # Барт найкраще працює з англ.
        try:
            # Обмежуємо текст для моделі до 1024 токенів
            summary = SUMMARIZER(text_to_process, max_length=50, min_length=10, do_sample=False)
            new_title = summary[0]['summary_text']
        except Exception as e:
            print(f"Помилка резюмування: {e}")
            
    article['generated_title'] = new_title
    
    # --- ПЕРЕКЛАД ЗГЕНЕРОВАНОГО/ОРИГІНАЛЬНОГО ЗАГОЛОВКА ---
    
    if lang_code == 'uk':
        article['ukr_title'] = new_title
        return article
        
    try:
        if lang_code == 'en' and EN_UK_TRANSLATOR:
            result = EN_UK_TRANSLATOR(new_title, max_length=150)
            
        elif lang_code == 'ru' and RU_UK_TRANSLATOR:
            result = RU_UK_TRANSLATOR(new_title, max_length=150)
            
        else:
            article['ukr_title'] = f"[НЕ ПЕРЕКЛАДЕНО/ЗГЕНЕРОВАНО З {lang_code}]"
            return article

        article['ukr_title'] = result[0]['translation_text']
        
    except Exception as e:
        article['ukr_title'] = f"[ПОМИЛКА ПЕРЕКЛАДУ: {e}]"
        
    return article

