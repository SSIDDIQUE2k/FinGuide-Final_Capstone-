# QUICK REFERENCE CARD - Financial Tools Django Site

## Start Here 🚀

```bash
# 1. Navigate to project
cd "/Users/shazibsiddique/Desktop/ai capstone project "

# 2. Activate environment
source .venv/bin/activate

# 3. Start Ollama (new terminal)
ollama serve

# 4. Run server (original terminal)
python manage.py runserver

# 5. Open browser
http://localhost:8000
```

## All URLs

| Path | Purpose |
|------|---------|
| `/` | Home page |
| `/chatbot/` | AI Chatbot |
| `/budget/` | Budget Calculator |
| `/calculator/` | Financial Calculators |
| `/api/chat/` | Chat API (POST) |
| `/api/calculate-budget/` | Budget API (POST) |
| `/api/calculate-compound-interest/` | Compound Interest API (POST) |
| `/api/calculate-loan/` | Loan Calculator API (POST) |
| `/api/calculate-investment-growth/` | Investment API (POST) |

## Page Features

### 🏠 Home
- Landing page with feature overview
- Links to all tools
- Getting started guide

### 💬 Chatbot
- Ask financial questions
- Real-time AI responses
- RAG-powered answers
- Grounded in 5,818 financial records

### 📊 Budget
- 50/30/20 budget method
- Customizable percentages
- Real-time calculations
- Helpful tips

### 🧮 Calculators
1. **Compound Interest** - Investment growth
2. **Loan Payment** - Monthly payments
3. **Investment Growth** - Long-term projections

## Key Technologies

- Django 4.2.26
- Ollama (llama3.2)
- LangChain 0.3.27
- Chroma Vector DB
- Pandas
- SQLite

## File Locations

- **Views**: `financial/views.py`
- **Templates**: `templates/financial/`
- **URLs**: `financial/urls.py`
- **Settings**: `financial_site/settings.py`
- **Data**: `Financial-Literacy-Compilation.csv`
- **Vector DB**: `chrome_langchain_db/`

## Common Tasks

### Customize Colors
Edit gradients in `templates/financial/base.html`

### Change AI Tone
Modify `SYSTEM_PROMPT` in `financial/views.py`

### Add New Calculator
1. Add view in `financial/views.py`
2. Add URL in `financial/urls.py`
3. Create template in `templates/financial/`
4. Add form HTML + JavaScript

### Deploy
1. Set `DEBUG = False` in settings.py
2. Set `ALLOWED_HOSTS`
3. Use PostgreSQL instead of SQLite
4. Deploy to Heroku, AWS, etc.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Can't connect to Ollama | Run `ollama serve` |
| Port 8000 taken | Use port 8001: `python manage.py runserver 8001` |
| Vector DB error | Delete `chrome_langchain_db/` folder |
| Import error | Make sure `vector_enhanced.py` has `get_retriever()` |

## Testing

```bash
# Run Django development server
python manage.py runserver

# Access chatbot
http://localhost:8000/chatbot/

# Try a calculation
http://localhost:8000/calculator/

# Check budget tool
http://localhost:8000/budget/
```

## Documentation

- **DJANGO_README.md** - Full documentation
- **COMPLETION_SUMMARY.md** - Project overview
- **PROJECT_OVERVIEW.txt** - Detailed stats

## Environment

- **Python**: 3.9
- **Virtual Env**: `.venv/`
- **Packages**: 40+ (see requirement.txt)
- **Database**: SQLite (`db.sqlite3`)

---

**Ready to deploy? Start with `python manage.py runserver`! 🚀**
