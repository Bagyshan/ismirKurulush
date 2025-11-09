from celery import shared_task
import requests
from config import settings
from .models import OrderRequest
from telegram_bot.bot import TelegramNotifier
import logging

logger = logging.getLogger(__name__)

# TELEGRAM_TOKEN = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
# TELEGRAM_CHAT_ID = getattr(settings, 'TELEGRAM_CHAT_ID', None)



@shared_task(bind=True)  # Добавляем bind=True для правильной работы
def send_order_to_telegram(self, order_id):
    """
    Задача для отправки заявки в Telegram канал
    """
    try:
        order = OrderRequest.objects.get(id=order_id)
        notifier = TelegramNotifier()
        
        success = notifier.send_order_notification(order)
        
        if success:
            # Помечаем как отправленное (опционально)
            order.is_processed = True
            order.save()
            return f"Заявка {order_id} отправлена в Telegram канал"
        else:
            # Повторяем задачу через 30 секунд в случае ошибки
            self.retry(countdown=30, max_retries=3)
            return f"Ошибка отправки заявки {order_id}"
            
    except OrderRequest.DoesNotExist:
        logger.error(f"Заявка {order_id} не найдена")
        return f"Заявка {order_id} не найдена"
    except Exception as e:
        logger.error(f"Ошибка отправки заявки {order_id}: {str(e)}")
        # Повторяем задачу через 30 секунд в случае ошибки
        self.retry(countdown=30, max_retries=3)
        return f"Ошибка отправки заявки {order_id}: {str(e)}"