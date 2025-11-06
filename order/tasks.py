from celery import shared_task
import requests
from django.conf import settings

TELEGRAM_TOKEN = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
TELEGRAM_CHAT_ID = getattr(settings, 'TELEGRAM_CHAT_ID', None)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_order_request_to_telegram(self, name, phone, comment, request_meta=None):
    """Отправляет сообщение о заявке в Telegram (через Bot API)

    Важно: TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID должны быть в settings/prod env
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        # логируем, но не падаем
        return {'status': 'skipped', 'reason': 'no-telegram-config'}

    text = (
        f"📦 *Новая заявка*\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: {phone}\n"
        f"📝 Комментарий: {comment or '-'}\n"
    )
    if request_meta:
        text += f"\n🔎 IP: {request_meta.get('ip')}\n"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }

    try:
        resp = requests.post(url, data=payload, timeout=10)
        resp.raise_for_status()
    except Exception as exc:
        raise self.retry(exc=exc)

    return {'status': 'sent'}
