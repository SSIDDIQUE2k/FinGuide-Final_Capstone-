#!/usr/bin/env python3
"""
🎯 Financial Literacy Assistant - ChatGPT Style
Simple, clean, and ready to use!
"""

import os
from dotenv import load_dotenv
load_dotenv()


print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║        💰 FINANCIAL LITERACY ASSISTANT - ChatGPT Style 💰         ║
║                                                                    ║
║         Your AI-powered financial advisor and educator            ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
""")

print("Initializing...")
print("-" * 70)

try:
    from langchain_ollama import OllamaLLM
    from langchain_core.prompts import ChatPromptTemplate
    print("✅ LangChain loaded")
    
    try:
        from vector_enhanced import retriever
        print("✅ Vector database loaded")
    except ImportError:
        from vector import retriever
        print("✅ Vector database loaded (original)")
    
    print("-" * 70)
    print()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure all dependencies are installed:")
    print("  pip install -r requirement.txt")
    exit(1)

# Initialize LLM
model_name = os.getenv("OLLAMA_MODEL", "tinyllama")
model = OllamaLLM(model=model_name)

# System prompt for ChatGPT-like responses
SYSTEM_PROMPT = """You are an exceptional financial advisor and educator, with the communication style of ChatGPT.

FINANCIAL DATA:
{context}

USER QUESTION: {question}

Guidelines for your response:
✓ Be warm, friendly, and conversational
✓ Use clear headers and formatting
✓ Provide real-world examples
✓ Give practical, actionable advice
✓ Explain financial terms in simple language
✓ Include step-by-step guidance when helpful
✓ Be encouraging and positive
✓ Use markdown formatting

Now provide your response:"""

prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
chain = prompt | model

# Example questions
EXAMPLES = [
    "How do I create a personal budget?",
    "What is compound interest?",
    "How do I start investing?",
    "What's an emergency fund?",
    "How do I build credit?",
]

def show_welcome():
    """Display welcome and options"""
    print("📚 ASK ABOUT:")
    print("   • Personal budgeting & savings")
    print("   • Investing & wealth building")
    print("   • Financial planning & goals")
    print("   • Money management & credit")
    print()
    print("📝 COMMANDS:")
    print("   • Type 'exit' to quit")
    print("   • Type 'help' to see examples")
    print()

def show_examples():
    """Show example questions"""
    print("\n📚 EXAMPLE QUESTIONS:\n")
    for i, question in enumerate(EXAMPLES, 1):
        print(f"   {i}. {question}")
    print()

# Main application loop
show_welcome()

print("=" * 70)
print()

question_count = 0

while True:
    try:
        # Get user input
        user_input = input("You: ").strip()
        
        # Empty input
        if not user_input:
            print("  (Please ask a question or type 'help' for examples)\n")
            continue
        
        # Exit command
        if user_input.lower() == 'exit':
            print(f"\n👋 Thank you for {question_count} questions! Stay financially smart! 💡\n")
            break
        
        # Help command
        if user_input.lower() == 'help':
            show_examples()
            continue
        
        question_count += 1
        
        # Show loading state
        print("\n🔍 Analyzing your question...")
        print("⏳ Generating response...\n")
        
        # Get relevant context
        context = retriever.invoke(user_input)
        
        # Generate response
        response = chain.invoke({
            "context": context,
            "question": user_input
        })
        
        # Display response
        print("💼 Financial Advisor:\n")
        print(response)
        print("\n" + "=" * 70 + "\n")
        
    except KeyboardInterrupt:
        print(f"\n\n👋 Goodbye! You asked {question_count} questions. Great learning session! 💡\n")
        break
    except EOFError:
        print("\n\n👋 Thank you for using the Financial Advisor! 💰\n")
        break
    except Exception as e:
        print(f"\n⚠️  Error: {str(e)}")
        print("Please try again or ask a different question.\n")
