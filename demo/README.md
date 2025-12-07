# Инструкция по запуску

## Требования

- Python 3.11+
- Установленные зависимости из `requirements.txt`

## Запуск

### 1. Запуск API сервера

```bash
cd demo
uvicorn server:app --host 127.0.0.1 --port 8001
```

### 2. Запуск Gradio интерфейса

В отдельном терминале:

```bash
cd demo
python gradio_app.py
```

Откройте браузер по адресу: `http://127.0.0.1:7860`
