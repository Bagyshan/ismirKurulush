from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg import openapi

SESSION_PARAM = openapi.Parameter(
    name='X-Session-Id',
    in_=openapi.IN_HEADER,
    type=openapi.TYPE_STRING,
    required=False,
    description='Session identifier для анонимной корзины (frontend должен подставлять при анонимном пользователе)'
)

class CustomAutoSchema(SwaggerAutoSchema):
    """
    Добавляет X-Session-Id как заголовок ко всем операциям.
    Если у конкретного view уже есть manual_parameters, они сохраняются.
    """
    def get_manual_parameters(self, *args, **kwargs):
        params = super().get_manual_parameters(*args, **kwargs) or []
        # Не дублируем, если уже есть
        if not any(p.name == 'X-Session-Id' for p in params):
            params.append(SESSION_PARAM)
        return params