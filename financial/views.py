from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pandas as pd
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector_enhanced import get_retriever

# Initialize LLM and retriever
model = OllamaLLM(model="llama3.2")
retriever = get_retriever()

# System prompt for financial assistant
SYSTEM_PROMPT = """You are a warm, friendly, and knowledgeable financial advisor AI. 
Your goal is to help people understand personal finance and make better financial decisions.

Guidelines for your responses:
1. Be conversational and encouraging, not robotic
2. Use clear, simple language - avoid jargon unless necessary
3. Provide practical, real-world examples
4. Give step-by-step guidance when relevant
5. Offer actionable advice they can implement today
6. Include formatting with headers, lists, and emphasis
7. Ask clarifying questions if needed
8. Provide resources or next steps
9. Be supportive of all financial situations
10. End with encouragement and an offer to help further

When answering questions, use the financial knowledge provided to ground your responses."""


def home(request):
    """Home page with navigation"""
    return render(request, 'financial/home.html')


def chatbot(request):
    """AI Chatbot page"""
    return render(request, 'financial/chatbot.html')


@csrf_exempt
def chat_api(request):
    """API endpoint for chatbot conversation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({'error': 'Empty message'}, status=400)
            
            # Retrieve context from vector database
            docs = retriever.invoke(user_message)
            context = "\n".join([doc.page_content for doc in docs])
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", """Based on the following financial context, answer the user's question.
Financial Context:
{context}

User Question: {question}""")
            ])
            
            # Generate response
            chain = prompt | model
            response = chain.invoke({
                "context": context,
                "question": user_message
            })
            
            return JsonResponse({'response': response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def budget(request):
    """Budget calculator page"""
    return render(request, 'financial/budget.html')


@csrf_exempt
def calculate_budget(request):
    """Calculate budget breakdown"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            income = float(data.get('income', 0))
            
            if income <= 0:
                return JsonResponse({'error': 'Income must be greater than 0'}, status=400)
            
            # Popular budget allocation method (50/30/20)
            needs = income * 0.50  # Essentials: housing, food, utilities
            wants = income * 0.30  # Discretionary: entertainment, dining
            savings = income * 0.20  # Savings and debt repayment
            
            # Get custom allocations if provided
            if 'needs_percent' in data:
                needs_percent = float(data.get('needs_percent', 50)) / 100
                wants_percent = float(data.get('wants_percent', 30)) / 100
                savings_percent = float(data.get('savings_percent', 20)) / 100
                
                needs = income * needs_percent
                wants = income * wants_percent
                savings = income * savings_percent
            
            result = {
                'income': round(income, 2),
                'needs': round(needs, 2),
                'wants': round(wants, 2),
                'savings': round(savings, 2),
                'breakdown': {
                    'needs_percent': round((needs / income) * 100, 1),
                    'wants_percent': round((wants / income) * 100, 1),
                    'savings_percent': round((savings / income) * 100, 1),
                }
            }
            
            return JsonResponse(result)
        except (ValueError, KeyError) as e:
            return JsonResponse({'error': f'Invalid input: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def calculator(request):
    """Financial calculator page"""
    return render(request, 'financial/calculator.html')


@csrf_exempt
def calculate_compound_interest(request):
    """Calculate compound interest"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            principal = float(data.get('principal', 0))
            rate = float(data.get('rate', 0))
            time = float(data.get('time', 0))
            frequency = int(data.get('frequency', 12))  # 1=annual, 12=monthly, 365=daily
            
            # Compound interest formula: A = P(1 + r/n)^(nt)
            rate_decimal = rate / 100
            amount = principal * ((1 + rate_decimal / frequency) ** (frequency * time))
            interest = amount - principal
            
            return JsonResponse({
                'principal': round(principal, 2),
                'rate': rate,
                'time': time,
                'final_amount': round(amount, 2),
                'interest_earned': round(interest, 2)
            })
        except (ValueError, KeyError) as e:
            return JsonResponse({'error': f'Invalid input: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def calculate_loan(request):
    """Calculate loan payment"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            principal = float(data.get('principal', 0))
            annual_rate = float(data.get('annual_rate', 0))
            months = int(data.get('months', 0))
            
            if months <= 0 or principal <= 0:
                return JsonResponse({'error': 'Invalid loan parameters'}, status=400)
            
            # Monthly payment formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]
            monthly_rate = (annual_rate / 100) / 12
            
            if monthly_rate == 0:
                monthly_payment = principal / months
            else:
                monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / \
                                 ((1 + monthly_rate) ** months - 1)
            
            total_payment = monthly_payment * months
            total_interest = total_payment - principal
            
            return JsonResponse({
                'principal': round(principal, 2),
                'annual_rate': annual_rate,
                'months': months,
                'monthly_payment': round(monthly_payment, 2),
                'total_payment': round(total_payment, 2),
                'total_interest': round(total_interest, 2)
            })
        except (ValueError, KeyError) as e:
            return JsonResponse({'error': f'Invalid input: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def calculate_investment_growth(request):
    """Calculate investment growth"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            initial = float(data.get('initial', 0))
            monthly_contribution = float(data.get('monthly_contribution', 0))
            annual_return = float(data.get('annual_return', 0))
            years = int(data.get('years', 0))
            
            monthly_rate = (annual_return / 100) / 12
            months = years * 12
            
            # Future value of initial investment
            fv_initial = initial * ((1 + monthly_rate) ** months)
            
            # Future value of monthly contributions
            if monthly_rate == 0:
                fv_contributions = monthly_contribution * months
            else:
                fv_contributions = monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate)
            
            total_value = fv_initial + fv_contributions
            total_invested = initial + (monthly_contribution * months)
            total_gain = total_value - total_invested
            
            return JsonResponse({
                'initial': round(initial, 2),
                'monthly_contribution': round(monthly_contribution, 2),
                'annual_return': annual_return,
                'years': years,
                'total_invested': round(total_invested, 2),
                'total_value': round(total_value, 2),
                'total_gain': round(total_gain, 2)
            })
        except (ValueError, KeyError) as e:
            return JsonResponse({'error': f'Invalid input: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
