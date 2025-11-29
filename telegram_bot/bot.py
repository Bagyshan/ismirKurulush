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
    
#     def _format_message(self, order):
#         space = ''
#         """Форматирование сообщения"""
#         return f"""
# 📞 <b>Новая заявка!</b> #{order.id}
# 🗂 <b>Тип заявки:</b> {order.request_type.name if order.request_type else 'Не указан'}

# 👤 <b>Имя:</b> {order.name}
# 📧 <b>Email:</b> <code>{order.email}</code>
# 📱 <b>Телефон:</b> <code>{order.phone}</code>
# 📝 <b>Комментарий:</b> {order.comment if order.comment else 'Не указан'}

# 🛒 <b>Корзина:</b> {space if order.cart else 'Не указана'}
# {''.join([f"   - {item.product.name} x{item.quantity} = {item.total_price}\n" for item in order.cart.items.all()]) if order.cart else ''}
#    <b>Общая сумма:</b> {order.cart.total_amount if order.cart else 'Не указано'}
# ⏰ <b>Время заявки:</b> {order.created_at.strftime('%d.%m.%Y %H:%M')}
#         """
    def _format_message(self, order):
        """Форматирование сообщения"""

        # отдельная сборка строк корзины
        if order.cart:
            cart_lines = [
                f"   - {item.product.name} x{item.quantity} = {item.total_price}"
                for item in order.cart.items.all()
            ]
            cart_text = "\n".join(cart_lines)
            cart_total = order.cart.total_amount
        else:
            cart_text = "Не указана"
            cart_total = "Не указано"

        return (
            "📞 <b>Новая заявка!</b> #" + str(order.id) + "\n"
            f"🗂 <b>Тип заявки:</b> {order.request_type.name if order.request_type else 'Не указан'}\n\n"
            f"👤 <b>Имя:</b> {order.name}\n"
            f"📧 <b>Email:</b> <code>{order.email}</code>\n"
            f"📱 <b>Телефон:</b> <code>{order.phone}</code>\n"
            f"📝 <b>Комментарий:</b> {order.comment if order.comment else 'Не указан'}\n\n"
            f"🛒 <b>Корзина:</b>\n{cart_text}\n"
            f"   <b>Общая сумма:</b> {cart_total}\n"
            f"⏰ <b>Время заявки:</b> {order.created_at.strftime('%d.%m.%Y %H:%M')}"
        )