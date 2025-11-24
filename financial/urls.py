from django.urls import path
from . import views

app_name = 'financial'

urlpatterns = [
    path('', views.home, name='home'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('api/chat/', views.chat_api, name='chat_api'),
    # Ollama-backed chatbot endpoint (expects POST JSON {"message": "..."})
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    # Compatibility alias used by some guides / earlier frontend code
    path('chatbot_api/', views.chatbot_api, name='chatbot_api_alias'),
    path('budget/', views.budget, name='budget'),
    path('api/calculate-budget/', views.calculate_budget, name='calculate_budget'),
    path('calculator/', views.calculator, name='calculator'),
    path('api/calculate-compound-interest/', views.calculate_compound_interest, name='compound_interest'),
    path('api/calculate-loan/', views.calculate_loan, name='calculate_loan'),
    path('api/calculate-investment-growth/', views.calculate_investment_growth, name='investment_growth'),
]
