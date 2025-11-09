import requests
import logging
from config import settings
import logging

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
    
    def send_order_notification(self, order):
        """Отправка уведомления о заявке в канал"""
        try:
            message = self._format_message(order)
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Уведомление о заявке {order.id} отправлено в Telegram")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки в Telegram: {e}")
            return False
    
    def _format_message(self, order):
        """Форматирование сообщения"""
        return f"""
📞 <b>Новая заявка!</b> #{order.id}

👤 <b>Имя:</b> {order.name}
📱 <b>Телефон:</b> <code>{order.phone}</code>
📝 <b>Комментарий:</b> {order.comment if order.comment else 'Не указан'}
⏰ <b>Время заявки:</b> {order.created_at.strftime('%d.%m.%Y %H:%M')}
        """