from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('<int:pk>/items/', views.BillItemList.as_view()),
    # path('<int:pk>/items/categories/', views.BillItemList.as_view()),
    path('items/', views.AllBillItemList.as_view()),
    path('items/<int:pk>/', views.BillItemDetail.as_view()),
    path('items/<int:pk>/categories/', views.BillItemCategoryList.as_view()),
    path('categories/', views.CategoryList.as_view()),
    path('categories/<int:pk>/', views.CategoryDetail.as_view()),
    path('', views.BillList.as_view()),
    path('<int:pk>', views.BillDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
