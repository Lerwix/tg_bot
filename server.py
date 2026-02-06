import json
import os
import uuid
from datetime import datetime

from flask import Flask, request, jsonify

JSON_FILE = "roles.json"

# Соответствие значений роли из формы тем ключам, которые использует бот
# В index.html: media, dev, support, qa, builder, moderator
# В боте:       media, developer, support, tester, builder, moderator
ROLE_MAP = {
    "dev": "developer",
    "qa": "tester",
}

ALL_ROLE_KEYS = ["media", "developer", "support", "tester", "builder", "moderator"]

app = Flask(__name__)


def load_roles():
    """Загрузить текущие заявки из JSON в ожидаемой ботом структуре."""
    if not os.path.exists(JSON_FILE):
        return {key: [] for key in ALL_ROLE_KEYS}

    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        # Если файл битый — начинаем заново, чтобы не ломать работу бота
        data = {}

    # Гарантируем наличие всех ключей
    for key in ALL_ROLE_KEYS:
        data.setdefault(key, [])

    return data


def save_roles(data: dict):
    """Сохранить структуру с заявками в JSON."""
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.post("/submit-application")
def submit_application():
    """Приём заявки с формы и сохранение в roles.json."""
    payload = request.get_json(silent=True) or {}

    # Значение роли, которое приходит из формы
    raw_role = payload.get("role")
    if not raw_role:
        return jsonify({"success": False, "error": "role is required"}), 400

    # Преобразуем к ключу, который понимает бот
    role_key = ROLE_MAP.get(raw_role, raw_role)
    if role_key not in ALL_ROLE_KEYS:
        return jsonify({"success": False, "error": f"unknown role: {raw_role}"}), 400

    # Собираем запись заявки
    application_id = str(uuid.uuid4())
    application = {
        "id": application_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "nickname": payload.get("nickname"),
        "age": payload.get("age"),
        "timezone": payload.get("timezone"),
        "telegram": payload.get("telegram"),
        "discord": payload.get("discord"),
        "role_raw": raw_role,
        "experience": payload.get("experience"),
        "minecraft_exp": payload.get("minecraft_exp"),
        "motivation": payload.get("motivation"),
        "portfolio": payload.get("portfolio"),
        "time_available": payload.get("time_available"),
        # Доп. поля, если вы их добавите в форме (необязательные)
        "source": payload.get("source"),
        "agreement": payload.get("agreement"),
    }

    data = load_roles()
    data.setdefault(role_key, [])
    data[role_key].append(application)
    save_roles(data)

    return jsonify({"success": True, "id": application_id})


if __name__ == "__main__":
    # Запуск dev-сервера Flask
    # index.html и статику можно отдавать любым веб-сервером;
    # главное — чтобы форма отправляла запрос на этот backend.
    app.run(host="0.0.0.0", port=8000, debug=True)

