"""
Simple keyword-based financial advice fallback (no AI required)
"""
import pandas as pd
import re

# Load financial data
try:
    df = pd.read_csv("Financial-Literacy-Compilation.csv")
    print(f"✅ Successfully loaded {len(df)} financial records for fallback")
except FileNotFoundError:
    print("❌ Error: Financial-Literacy-Compilation.csv not found!")
    df = None

def simple_search(query, top_k=3):
    """
    Simple keyword-based search - no embeddings required
    Returns relevant financial information based on keyword matching
    """
    if df is None or df.empty:
        return "Unable to access financial database."
    
    query_lower = query.lower()
    
    # Extract keywords (remove common words)
    stop_words = {'what', 'is', 'a', 'an', 'the', 'how', 'to', 'do', 'does', 'can', 'could', 'should', 'would', 'about', 'tell', 'me', 'explain'}
    words = [w for w in re.findall(r'\w+', query_lower) if w not in stop_words and len(w) > 2]
    
    if not words:
        return "Please ask a specific financial question."
    
    # Score each row based on keyword matches
    scores = []
    for idx, row in df.iterrows():
        score = 0
        row_text = " ".join([str(val).lower() for val in row.values if pd.notna(val)])
        
        for word in words:
            # Count occurrences of each keyword
            score += row_text.count(word)
        
        if score > 0:
            scores.append((score, idx, row))
    
    if not scores:
        return "I couldn't find specific information about that. Try asking about common topics like budgeting, savings, investing, or debt."
    
    # Sort by score and get top results
    scores.sort(reverse=True, key=lambda x: x[0])
    top_results = scores[:top_k]
    
    # Format response
    response = "📚 **Here's what I found in our financial database:**\n\n"
    
    for i, (score, idx, row) in enumerate(top_results, 1):
        # Get the most relevant fields from the row
        relevant_text = []
        for col in df.columns:
            val = str(row[col])
            if pd.notna(row[col]) and len(val) > 10 and any(word in val.lower() for word in words):
                relevant_text.append(f"**{col}**: {val[:300]}")
        
        if relevant_text:
            response += f"{i}. " + " | ".join(relevant_text[:2]) + "\n\n"
    
    response += "\n💡 **Tip:** This information is educational. For personalized financial advice, consult a licensed financial advisor."
    
    return response
