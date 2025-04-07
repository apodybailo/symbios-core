import requests
import logging

# Налаштування логів
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "mistral:latest"

def generate_with_mistral(prompt: str) -> str:
    url = f"{OLLAMA_URL}/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    logger.info(f"[Mistral] Надсилаю запит до Ollama з prompt: {prompt}")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)

        if response.status_code == 200:
            result = response.json()
            output = result.get("response", "").strip()
            logger.info(f"[Mistral] Отримано відповідь: {output}")
            return output if output else "⚠️ Відповідь порожня."
        else:
            logger.error(f"[Mistral] Помилка HTTP {response.status_code}: {response.text}")
            return f"❌ Помилка від Mistral: HTTP {response.status_code}"

    except requests.exceptions.ConnectionError:
        logger.exception("[Mistral] Неможливо підключитись до Ollama. Чи запущений ollama serve?")
        return "❌ Mistral недоступний. Перевір, чи запущено ollama serve."

    except Exception as e:
        logger.exception(f"[Mistral] Невідома помилка: {e}")
        return f"❌ Виникла помилка: {e}"

# 🔍 Тестовий запуск із CLI
if __name__ == "__main__":
    res = generate_with_mistral("Що таке Шлях Воїна?")
    print("👉", res)
