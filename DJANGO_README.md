# 💰 Financial Tools - Django Web Application

A full-featured Django web application with three powerful pages for financial management and education.

## Features

### 🏠 Home Page
- Beautiful landing page with quick links to all tools
- Feature highlights and getting started guide
- Responsive grid layout

### 💬 AI Financial Chatbot
- Interactive chatbot powered by Ollama LLM (llama3.2)
- Leverages RAG (Retrieval-Augmented Generation) pipeline
- Grounded responses using 5,818 financial literacy records
- Real-time chat interface with message history
- Warm, conversational tone with practical financial advice

### 📊 Budget Calculator
- 50/30/20 budget allocation method
  - **50%**: Needs (housing, food, utilities)
  - **30%**: Wants (entertainment, dining)
  - **20%**: Savings & debt repayment
- Customizable allocation percentages
- Clear breakdown with visual percentages
- Practical tips for budget management

### 🧮 Financial Calculator
Three powerful calculators:

1. **Compound Interest Calculator**
   - Calculate investment growth over time
   - Adjustable compounding frequency (annual, semi-annual, quarterly, monthly, daily)
   - Shows interest earned and final amount

2. **Loan Payment Calculator**
   - Calculate monthly loan payments
   - Displays total interest and total payment
   - Based on standard amortization formula

3. **Investment Growth Calculator**
   - Projects investment growth with monthly contributions
   - Shows total invested vs. total value
   - Calculates investment gains

## Technology Stack

- **Backend**: Django 4.2.26
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **AI/ML**: 
  - Ollama LLM (llama3.2)
  - LangChain 0.3.27
  - Chroma Vector Database
  - mxbai-embed-large Embeddings
- **Data Processing**: Pandas 2.3.3
- **Database**: SQLite

## Project Structure

```
financial_site/
├── financial/                      # Main app
│   ├── views.py                   # All view functions (200+ lines)
│   ├── urls.py                    # URL routing
│   └── apps.py
├── financial_site/
│   ├── settings.py                # Django configuration
│   ├── urls.py                    # Main URL config
│   └── wsgi.py
├── templates/financial/
│   ├── base.html                  # Base template with navigation
│   ├── home.html                  # Home page
│   ├── chatbot.html               # AI Chatbot page
│   ├── budget.html                # Budget calculator page
│   └── calculator.html            # Financial calculators page
├── vector_enhanced.py             # Vector database setup
├── app.py                         # Original CLI chatbot (optional)
├── Financial-Literacy-Compilation.csv  # Financial data (5,818 records)
├── requirement.txt                # Python dependencies
├── manage.py                      # Django management
└── run_server.sh                  # Server startup script
```

## Installation & Setup

### 1. Prerequisites
- Python 3.9+
- Ollama installed and running locally
- Virtual environment (recommended)

### 2. Install Dependencies

```bash
cd "/Users/shazibsiddique/Desktop/ai capstone project "
source .venv/bin/activate
pip install -r requirement.txt
```

### 3. Initialize Django

```bash
python manage.py migrate
```

### 4. Start Ollama (in a separate terminal)

```bash
ollama serve
```

This starts the Ollama server that powers the AI chatbot.

### 5. Start Django Development Server

**Option A: Using the startup script**
```bash
chmod +x run_server.sh
./run_server.sh
```

**Option B: Manual startup**
```bash
python manage.py runserver
```

The server will start on `http://localhost:8000`

## Usage

### Home Page (`/`)
- Landing page with overview of all features
- Quick navigation to each tool

### AI Chatbot (`/chatbot/`)
1. Type your financial question in the input box
2. Press Enter or click "Send"
3. The AI will respond with personalized advice
4. Continue the conversation naturally

**Example Questions:**
- "What is a budget?"
- "How can I improve my credit score?"
- "What's the difference between needs and wants?"
- "How do I start investing?"
- "What is compound interest?"

### Budget Calculator (`/budget/`)
1. Enter your monthly income
2. Choose between standard 50/30/20 or custom percentages
3. Click "Calculate Budget"
4. View your budget breakdown by category

### Financial Calculator (`/calculator/`)

**Compound Interest:**
- Enter principal, rate, and time
- Choose compounding frequency
- Get final amount and interest earned

**Loan Payment:**
- Enter loan amount, interest rate, and term
- Get monthly payment, total payment, and total interest

**Investment Growth:**
- Enter initial investment and monthly contributions
- Set expected annual return and period
- View projected growth and total gains

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Home page |
| GET | `/chatbot/` | Chatbot interface |
| POST | `/api/chat/` | Chat API |
| GET | `/budget/` | Budget calculator |
| POST | `/api/calculate-budget/` | Budget calculation |
| GET | `/calculator/` | Financial calculator |
| POST | `/api/calculate-compound-interest/` | Compound interest calculation |
| POST | `/api/calculate-loan/` | Loan payment calculation |
| POST | `/api/calculate-investment-growth/` | Investment projection |

## Configuration

### AI Model Settings (in `financial/views.py`)
- Model: `llama3.2` (via Ollama)
- Embeddings: `mxbai-embed-large`
- Vector Store: Chroma (at `./chrome_langchain_db`)
- Top-k Retrieval: 5 documents

### Budget Calculator (default in `financial/views.py`)
- Default allocation: 50% needs, 30% wants, 20% savings
- Fully customizable through the UI

## Troubleshooting

### "Cannot connect to Ollama"
- Ensure Ollama is running: `ollama serve`
- Check if ollama is accessible at `http://localhost:11434`
- Default model `llama3.2` must be installed: `ollama pull llama3.2`

### "Vector database not found"
- The database is auto-created on first run at `./chrome_langchain_db`
- If corrupted, delete the directory and restart the server

### "Financial-Literacy-Compilation.csv not found"
- Ensure the CSV file is in the project root directory
- The file should be 429 KB and contain 5,818 records

### Chat API errors
- Check browser console for detailed error messages
- Ensure CSRF token is included in POST requests (automatic via Django middleware)

## Customization

### Change AI Tone
Edit `SYSTEM_PROMPT` in `financial/views.py` to customize the chatbot's personality.

### Add New Calculators
1. Create a new function in `financial/views.py` with `@csrf_exempt` decorator
2. Add the route to `financial/urls.py`
3. Create HTML form and JavaScript in a template

### Modify Templates
- Edit `.html` files in `templates/financial/` directory
- CSS is embedded in `base.html` for easy customization
- All pages use gradient backgrounds and modern design

## Performance Notes

- Vector database queries: ~50-200ms
- LLM response generation: 3-10 seconds (depends on Ollama model)
- Chat history: Stored in browser session
- No database storage of conversations

## Security Notes

- CSRF protection enabled on all POST endpoints
- SQL injection prevention via ORM
- XSS protection through template escaping
- Debug mode disabled in production

## Browser Support

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Responsive design

## Dependencies

See `requirement.txt` for full list:
- django
- langchain
- langchain-ollama
- pandas
- opensearch-py
- langchain-community

## Future Enhancements

- User authentication and saved preferences
- Conversation history export (PDF/CSV)
- Mobile app
- Voice input/output
- Chart visualizations for calculations
- Dark mode
- Multi-language support
- Advanced budget tracking with time series
- Financial goal setting and tracking

## Support

For issues, questions, or suggestions, check the original project documentation or contact the development team.

## License

This project uses open-source components. See individual packages for licensing details.

---

**Happy Financial Planning! 💰📊🚀**
