from django.urls import path
from app.views import index, processing, keywords, save_keywords, video_selection



urlpatterns = [
    path('', index, name='index'),
    path('processing/', processing, name='processing'),
    path('keywords/', keywords, name='keywords'),
    path('save_keywords/', save_keywords, name='save_keywords'),
    path('video_selection/', video_selection, name='video_selection'),
]
