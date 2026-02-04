"""
chatbot.py — AI Financial Assistant (Read-Only)
Uses Groq API for natural language financial advice
"""

import os
from groq import Groq

# Initialize Groq client
def get_groq_client():
    """Initialize Groq client with API key from environment"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    return Groq(api_key=api_key)


def get_financial_context(user_id, get_summary_func, get_total_func, get_expense_cat_func, get_transactions_func):
    """
    Gather read-only financial data for the chatbot context
    
    Args:
        user_id: Current user's ID
        get_summary_func: Function to get transaction summary
        get_total_func: Function to get totals by type
        get_expense_cat_func: Function to get expense breakdown
        get_transactions_func: Function to get all transactions
    
    Returns:
        dict: Financial context data
    """
    try:
        summary = get_summary_func(user_id)
        total_income = get_total_func(user_id, 'Income')
        total_expense = get_total_func(user_id, 'Expense')
        expense_by_category = get_expense_cat_func(user_id)
        transactions = get_transactions_func(user_id)
        
        # Get recent transactions (last 10)
        recent_txns = []
        for t in transactions[:10]:
            recent_txns.append({
                'date': t.date.strftime('%Y-%m-%d'),
                'type': t.transaction_type,
                'category': t.category,
                'amount': float(t.amount),
                'description': t.description if t.description else 'N/A'
            })
        
        # Format expense breakdown
        expense_breakdown = []
        if expense_by_category:
            for cat, amt in expense_by_category.items():
                expense_breakdown.append({'category': cat, 'amount': float(amt)})
        
        context = {
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'balance': float(summary['balance']),
            'transaction_count': summary['transaction_count'],
            'expense_breakdown': expense_breakdown,
            'recent_transactions': recent_txns
        }
        
        return context
    except Exception as e:
        print(f"Error gathering financial context: {e}")
        return None


def format_context_for_prompt(context):
    """Format financial context into a readable string for the AI"""
    if not context:
        return "No financial data available."
    
    lines = [
        f"📊 FINANCIAL SUMMARY:",
        f"• Total Income: ₹{context['total_income']:,.2f}",
        f"• Total Expense: ₹{context['total_expense']:,.2f}",
        f"• Current Balance: ₹{context['balance']:,.2f}",
        f"• Total Transactions: {context['transaction_count']}",
        ""
    ]
    
    if context['expense_breakdown']:
        lines.append("💸 EXPENSE BREAKDOWN:")
        sorted_expenses = sorted(context['expense_breakdown'], key=lambda x: x['amount'], reverse=True)
        for item in sorted_expenses[:5]:  # Top 5 categories
            lines.append(f"  - {item['category']}: ₹{item['amount']:,.2f}")
        lines.append("")
    
    if context['recent_transactions']:
        lines.append("📜 RECENT TRANSACTIONS (Last 10):")
        for txn in context['recent_transactions'][:5]:  # Show 5 most recent
            emoji = "🟢" if txn['type'] == 'Income' else "🔴"
            lines.append(f"  {emoji} {txn['date']} | {txn['category']}: ₹{txn['amount']:,.2f}")
        lines.append("")
    
    return "\n".join(lines)


def get_chatbot_response(user_message, context, conversation_history=None):
    """
    Get AI response using Groq API
    
    Args:
        user_message: User's question/message
        context: Financial context dictionary
        conversation_history: List of previous messages (optional)
    
    Returns:
        str: AI assistant's response
    """
    try:
        client = get_groq_client()
        
        # Build system prompt with financial context
        context_str = format_context_for_prompt(context)
        
        system_prompt = f"""You are a friendly, supportive AI financial advisor for a personal budget monitoring app.

**YOUR DATA (READ-ONLY):**
{context_str}

**YOUR ROLE:**
- Provide personalized financial advice based on the user's data above
- Explain spending patterns clearly and simply
- Suggest realistic savings opportunities (5-15% improvements)
- Highlight high-expense categories
- Encourage better budgeting habits
- Be supportive, non-judgmental, and motivating
- Use simple English, avoid finance jargon

**ABSOLUTE RULES:**
1. NEVER give investment, stock, crypto, or trading advice
2. NEVER give tax or legal advice
3. NEVER suggest loans or credit cards
4. NEVER ask for personal banking information
5. NEVER predict future income
6. You are READ-ONLY — you cannot modify transactions or data
7. Keep responses concise (3-5 sentences or short bullet points)
8. Use minimal emojis (💡📊💸👍)
9. Ask ONE helpful follow-up question per response (optional)

**RESPONSE STYLE:**
- Short paragraphs or bullet points
- Clear, actionable insights
- Friendly and encouraging tone
- Focus on small, achievable improvements

Remember: You're helping students/freshers manage money better, not giving professional financial advice."""

        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",  # Fast and capable model
            temperature=0.7,
            max_tokens=500,
            top_p=0.9
        )
        
        response = chat_completion.choices[0].message.content
        return response
        
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower():
            return "❌ **Groq API Key Error**: Please set your GROQ_API_KEY environment variable. Get your free key at https://console.groq.com/keys"
        elif "rate" in error_msg.lower() or "limit" in error_msg.lower():
            return "⏳ **Rate Limit**: Too many requests. Please wait a moment and try again."
        else:
            return f"❌ **Error**: {error_msg}\n\nPlease check your Groq API configuration."


def get_quick_insight(context):
    """Generate a quick financial insight without user input"""
    if not context or context['transaction_count'] == 0:
        return "👋 Start adding transactions to get personalized financial insights!"
    
    try:
        client = get_groq_client()
        context_str = format_context_for_prompt(context)
        
        prompt = f"""Based on this financial data, give ONE brief, actionable insight (2-3 sentences max):

{context_str}

Focus on the most important observation and one specific tip."""

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful financial advisor. Be concise and actionable."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=150
        )
        
        return "💡 " + chat_completion.choices[0].message.content
        
    except:
        # Fallback insight
        if context['balance'] < 0:
            return "💡 Your expenses exceed income. Try identifying your top 2 expense categories and reducing them by 10%."
        elif context['expense_breakdown']:
            top_cat = max(context['expense_breakdown'], key=lambda x: x['amount'])
            return f"💡 {top_cat['category']} is your highest expense at ₹{top_cat['amount']:,.0f}. Small reductions here can significantly improve your savings."
        else:
            return "💡 Great start! Keep tracking your transactions to get personalized insights."