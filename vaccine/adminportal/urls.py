from django.urls import path
from .views import send_email
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('send_mail/', send_email, name="send_mail"),
    path('list/<str:date>/<int:slot_no>/',views.list,name="list"),
    path('slots/',views.slots_created,name="slots")
]