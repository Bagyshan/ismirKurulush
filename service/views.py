from django.shortcuts import render
from rest_framework import generics
from .models import Service
from .serializers import ServiceListSerializer, ServiceDetailSerializer
# Create your views here.



class ServiceListView(generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceListSerializer
    pagination_class = None 

class ServiceDetailView(generics.RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceDetailSerializer
    lookup_field = 'pk'