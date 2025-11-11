import datetime

# Отримання поточної дати та часу (UTC, оскільки GitHub Actions працює в UTC)
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

# 1. Створення простого HTML-контенту
# Цей контент буде вставлено у ваш індексний файл.
test_content = f"""
            <h2>🟢 Скрипт успішно виконано!</h2>
            <p>Це підтвердження того, що GitHub Actions запустив Python-скрипт.</p>
            <p>Час останнього автоматичного запуску: <strong>{current_time}</strong></p>
            <p>Тепер ми можемо інтегрувати складнішу логіку (PyTorch).</p>
"""

# 2. Формування повного HTML-файлу
# Ми використовуємо мінімальний каркас для перезапису index.html
final_html_content = f"""
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>Тест Автоматизації GitHub Actions</title>
</head>
<body>
    <div style="max-width: 600px; margin: 50px auto; padding: 20px; border: 1px solid #ccc;">
        {test_content}
    </div>
</body>
</html>
"""

# 3. Перезапис index.html
try:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html_content)
    print(f"index.html успішно оновлено! Час: {current_time}")

except Exception as e:
    print(f"ПОМИЛКА при записі файлу: {e}")
