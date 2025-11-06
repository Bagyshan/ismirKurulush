from django.urls import path
from .views import ProductListView, ProductDetailView, CategoryListView, BrandListView, SortingOptionsView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('brands/', BrandListView.as_view(), name='brand-list'),
    path("sorting-options/", SortingOptionsView.as_view(), name="sorting-options"),
]