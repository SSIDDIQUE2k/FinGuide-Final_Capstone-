import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pandas as pd
import logging
import subprocess
from django.conf import settings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector_enhanced import get_retriever

logger = logging.getLogger(__name__)

# Initialize LLM and retriever (used by the LangChain chat_api)
try:
    # Ensure we're using localhost without any proxy
    import os
    os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
    os.environ['no_proxy'] = 'localhost,127.0.0.1'
    
    # Use shorter timeout for memory-constrained environments
    model = OllamaLLM(
        model=settings.OLLAMA_MODEL or "llama3.2:latest", 
        base_url=settings.OLLAMA_API_BASE,
        timeout=60,  # Reduced from 30 to give more time but not too long
        num_predict=256  # Limit response length to reduce memory usage
    )
    logger.info('LLM initialized successfully with model: %s', settings.OLLAMA_MODEL)
except Exception as e:
    model = None
    logger.warning('LLM initialization failed: %s', str(e))

retriever = None
try:
    retriever = get_retriever()
    logger.info('Vector retriever initialized successfully')
except Exception as e:
    retriever = None
    logger.warning('Vector retriever initialization failed: %s', str(e))

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
    return render(request, 'financial/home.html')


def chatbot(request):
    return render(request, 'financial/chatbot.html')


@csrf_exempt
def chat_api(request):
    """LangChain-backed chat endpoint (POST JSON with 'message')."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Empty message'}, status=400)

        # Retrieve context if retriever available
        context = ""
        if retriever:
            try:
                docs = retriever.invoke(user_message)
                context = "\n".join([doc.page_content for doc in docs])
            except Exception:
                context = ""

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", """Based on the following financial context, answer the user's question.
Financial Context:
{context}

User Question: {question}""")
        ])

        if model is None:
            # Provide helpful fallback when Ollama is not available
            fallback_msg = (
                "I apologize, but the AI service is currently unavailable. "
                "This typically means Ollama is not running on the server.\n\n"
                "However, I can still provide some guidance based on your question about: " + user_message + "\n\n"
            )
            
            if context:
                # Use retrieved context to provide a helpful response
                fallback_msg += "Here's some relevant information from our financial database:\n\n" + context[:500]
            else:
                fallback_msg += "Please contact the administrator to enable the AI chatbot service."
            
            return JsonResponse({'response': fallback_msg})

        try:
            # Use direct Ollama API call with streaming to reduce memory
            ollama_response = ollama_chat_direct(user_message, context)
            if ollama_response.startswith('ERROR:'):
                # If Ollama fails, use context-based fallback
                if context:
                    fallback_msg = (
                        "⚠️ The AI service is temporarily unavailable due to server resources.\n\n" +
                        "📚 Here's relevant information from our financial knowledge base:\n\n" +
                        context[:600] + "\n\n" +
                        "💡 **Tip:** For complex questions, try breaking them into smaller parts."
                    )
                    return JsonResponse({'response': fallback_msg})
                else:
                    return JsonResponse({
                        'error': 'AI service temporarily unavailable',
                        'details': ollama_response
                    }, status=503)
            
            return JsonResponse({'response': ollama_response})
        except Exception as llm_error:
            logger.error('LLM invocation error: %s', str(llm_error))
            # Provide context-based fallback if LLM fails
            if context:
                fallback_msg = (
                    "⚠️ The AI encountered an error, but here's relevant information from our database:\n\n" +
                    context[:800] + "\n\n" +
                    "Please try rephrasing your question or contact support if the issue persists."
                )
                return JsonResponse({'response': fallback_msg})
            raise
            
    except Exception as e:
        logger.exception('chat_api error')
        error_msg = str(e)
        if 'Connection refused' in error_msg or 'bad gateway' in error_msg.lower():
            return JsonResponse({
                'error': 'AI service is unavailable. Please ensure Ollama is running on the server.',
                'details': 'Connection to Ollama failed'
            }, status=503)
        return JsonResponse({'error': f'Server error: {error_msg}'}, status=500)


def ollama_chat_direct(user_message, context=""):
    """
    Memory-efficient direct call to Ollama API with context injection.
    Returns formatted response or ERROR: prefix on failure.
    """
    base = (settings.OLLAMA_API_BASE or '').rstrip('/')
    if not base:
        return 'ERROR: OLLAMA_API_BASE not configured'
    
    # Construct prompt with context
    if context:
        full_prompt = f"""{SYSTEM_PROMPT}

Financial Context:
{context[:1000]}

User Question: {user_message}

Provide a helpful, concise response (max 250 words):"""
    else:
        full_prompt = f"""{SYSTEM_PROMPT}

User Question: {user_message}

Provide a helpful, concise response (max 250 words):"""
    
    payload = {
        'model': settings.OLLAMA_MODEL,
        'prompt': full_prompt,
        'stream': False,
        'options': {
            'num_predict': 300,  # Limit tokens to reduce memory
            'temperature': 0.7,
            'top_p': 0.9
        }
    }
    
    url = f"{base}/api/generate"
    
    try:
        logger.info('Calling Ollama with reduced memory settings')
        # Short timeout to prevent worker hanging
        resp = requests.post(
            url, 
            json=payload, 
            timeout=45,  # 45 second timeout
            proxies={'http': None, 'https': None}
        )
        
        if resp.status_code == 200:
            try:
                return resp.json().get('response', 'No response from model')
            except Exception:
                return resp.text
        else:
            logger.error('Ollama returned %s: %s', resp.status_code, resp.text[:200])
            return f'ERROR: Ollama returned status {resp.status_code}'
            
    except requests.exceptions.Timeout:
        logger.error('Ollama request timed out after 45s')
        return 'ERROR: Request timed out - server may be overloaded'
    except requests.exceptions.ConnectionError as e:
        logger.error('Cannot connect to Ollama: %s', str(e))
        return 'ERROR: Cannot connect to Ollama service'
    except Exception as e:
        logger.exception('Ollama request failed')
        return f'ERROR: {str(e)}'


def ollama_chat(prompt):
    """Call Ollama's /api/generate endpoint and return the text response."""
    payload = {
        'model': settings.OLLAMA_MODEL, 
        'prompt': prompt,
        'stream': False,
        'options': {'num_predict': 256}  # Limit response length
    }

    # Common endpoint candidates used by different Ollama versions / API layers
    endpoints = [
        '/api/generate',
        '/v1/generate',
        '/api/v1/generate',
        '/generate'
    ]

    base = (settings.OLLAMA_API_BASE or '').rstrip('/')
    if not base:
        logger.error('OLLAMA_API_BASE not set')
        return 'Ollama error: OLLAMA_API_BASE not configured'

    last_exc = None
    for ep in endpoints:
        url = f"{base}{ep}"
        try:
            logger.debug('Trying Ollama endpoint: %s', url)
            # Disable proxies for direct connection (fixes local proxy issues)
            # Use shorter timeout for memory-constrained environments
            resp = requests.post(url, json=payload, timeout=30, proxies={'http': None, 'https': None})
            # If we get a successful response, return its text
            if resp.status_code >= 200 and resp.status_code < 300:
                try:
                    return resp.json().get('response', '')
                except Exception:
                    # Non-JSON but successful
                    return resp.text

            # Record non-2xx for logging and continue to next candidate
            logger.warning('Ollama endpoint %s returned %s: %s', url, resp.status_code, resp.text[:400])
            last_exc = requests.exceptions.HTTPError(f"{resp.status_code} for {url}")
        except requests.exceptions.ConnectionError as e:
            last_exc = e
            logger.warning('Connection failed for %s: %s (Ollama may not be running)', url, str(e))
        except requests.exceptions.Timeout as e:
            last_exc = e
            logger.warning('Timeout contacting %s: %s', url, str(e))
        except Exception as e:
            last_exc = e
            logger.warning('Failed contacting %s: %s', url, str(e))
            # try the next endpoint

    # If we're here, all attempts failed
    logger.error('All Ollama endpoint attempts failed; last error: %s', str(last_exc))
    
    # Provide more helpful error message
    if isinstance(last_exc, requests.exceptions.ConnectionError):
        return 'Unable to connect to Ollama service. Please ensure Ollama is installed and running on the server.'
    return f'Ollama service unavailable: {str(last_exc)}'


def chatbot_api(request):
    """Compatibility endpoint for simple GET requests used in the guide.

    Accepts either GET?message=... or POST JSON {"message": "..."}.
    Returns JSON {"response": "..."} on success or {"error": "..."}.
    """
    if request.method == 'GET':
        user_msg = request.GET.get('message', '').strip()
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_msg = (data.get('message') or '').strip()
        except Exception:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    if not user_msg:
        return JsonResponse({'response': ''})

    reply = ollama_chat(user_msg)
    return JsonResponse({'response': reply})


def budget(request):
    return render(request, 'financial/budget.html')


@csrf_exempt
def calculate_budget(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            income = float(data.get('income', 0))

            if income <= 0:
                return JsonResponse({'error': 'Income must be greater than 0'}, status=400)

            needs = income * 0.50
            wants = income * 0.30
            savings = income * 0.20

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
            logger.exception('calculate_budget error')
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


def calculator(request):
    return render(request, 'financial/calculator.html')


@csrf_exempt
def calculate_compound_interest(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            principal = float(data.get('principal', 0))
            rate = float(data.get('rate', 0))
            time = float(data.get('time', 0))
            frequency = int(data.get('frequency', 12))

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
            logger.exception('calculate_compound_interest error')
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def calculate_loan(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            principal = float(data.get('principal', 0))
            annual_rate = float(data.get('annual_rate', 0))
            months = int(data.get('months', 0))

            if months <= 0 or principal <= 0:
                return JsonResponse({'error': 'Invalid loan parameters'}, status=400)

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
            logger.exception('calculate_loan error')
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def calculate_investment_growth(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            initial = float(data.get('initial', 0))
            monthly_contribution = float(data.get('monthly_contribution', 0))
            annual_return = float(data.get('annual_return', 0))
            years = int(data.get('years', 0))

            monthly_rate = (annual_return / 100) / 12
            months = years * 12

            fv_initial = initial * ((1 + monthly_rate) ** months)

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
            logger.exception('calculate_investment_growth error')
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)
