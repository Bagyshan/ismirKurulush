from rest_framework import serializers
from .models import Service, Possibilities, Advantages, WorkProcess

class PossibilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Possibilities
        fields = ['id', 'name']
class AdvantagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advantages
        fields = ['id', 'name']
class WorkProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkProcess
        fields = ['id', 'step_number', 'description']

class ServiceListSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'icon', 'description']

    def get_icon(self, obj):
        request = self.context.get("request")
        if not obj.icon:
            return None
        if request:
            return request.build_absolute_uri(obj.icon.url)
        # fallback если сериализатор используется без HTTP-контекста
        from django.conf import settings
        return f"{settings.SITE_DOMAIN}{obj.icon.url}"

class ServiceDetailSerializer(serializers.ModelSerializer):
    possibilities = PossibilitiesSerializer(many=True, read_only=True)
    advantages = AdvantagesSerializer(many=True, read_only=True)
    work_process = WorkProcessSerializer(many=True, read_only=True)
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            'id', 'icon', 'name', 'description', 'price', 
            'unit_of_measurement', 'term', 
            'possibilities', 'advantages', 'work_process'
        ]

    def get_icon(self, obj):
        request = self.context.get("request")
        if not obj.icon:
            return None
        if request:
            return request.build_absolute_uri(obj.icon.url)
        # fallback если сериализатор используется без HTTP-контекста
        from django.conf import settings
        return f"{settings.SITE_DOMAIN}{obj.icon.url}"