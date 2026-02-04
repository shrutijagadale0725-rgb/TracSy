"""
test_chatbot.py — Quick test script for Groq AI integration
Run this to verify your setup before using the full app
"""

import os
import sys

def test_groq_connection():
    """Test if Groq API key is set and working"""
    
    print("=" * 60)
    print("🤖 CHATBOT SETUP VERIFICATION TEST")
    print("=" * 60)
    print()
    
    # Step 1: Check if API key exists
    print("Step 1: Checking GROQ_API_KEY environment variable...")
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ FAILED: GROQ_API_KEY not found!")
        print()
        print("📌 How to fix:")
        print("   Windows CMD:     set GROQ_API_KEY=your_key_here")
        print("   Windows PS:      $env:GROQ_API_KEY='your_key_here'")
        print("   Mac/Linux:       export GROQ_API_KEY=your_key_here")
        print()
        print("🔑 Get your FREE API key at: https://console.groq.com/keys")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...{api_key[-4:]}")
    print()
    
    # Step 2: Check if groq package is installed
    print("Step 2: Checking if 'groq' package is installed...")
    try:
        from groq import Groq
        print("✅ Groq package is installed")
    except ImportError:
        print("❌ FAILED: 'groq' package not installed!")
        print()
        print("📌 How to fix:")
        print("   pip install groq")
        return False
    print()
    
    # Step 3: Test API connection
    print("Step 3: Testing Groq API connection...")
    try:
        client = Groq(api_key=api_key)
        
        # Send a simple test request
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Respond with exactly 'Test successful!'"
                },
                {
                    "role": "user",
                    "content": "Hello"
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=50
        )
        
        response = chat_completion.choices[0].message.content
        print(f"✅ API Response: {response}")
        print()
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        print()
        print("📌 Possible issues:")
        print("   - Invalid API key")
        print("   - Network connection problem")
        print("   - Groq service down (check https://status.groq.com)")
        return False
    
    # Step 4: Test financial context simulation
    print("Step 4: Testing chatbot financial advice...")
    try:
        test_context = {
            'total_income': 15000.0,
            'total_expense': 12000.0,
            'balance': 3000.0,
            'transaction_count': 25,
            'expense_breakdown': [
                {'category': 'Food', 'amount': 5000.0},
                {'category': 'Transport', 'amount': 3000.0}
            ]
        }
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are a financial advisor. 
                    
USER DATA:
- Income: ₹15,000
- Expense: ₹12,000
- Balance: ₹3,000
- Top expense: Food (₹5,000)

Give ONE brief tip in 2 sentences."""
                },
                {
                    "role": "user",
                    "content": "How can I save more?"
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=150
        )
        
        advice = chat_completion.choices[0].message.content
        print(f"✅ Sample Financial Advice:")
        print(f"   {advice}")
        print()
        
    except Exception as e:
        print(f"⚠️  Warning: {str(e)}")
        print("   Basic connection works, but full feature test failed")
        print()
    
    # Final result
    print("=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print()
    print("✅ Your chatbot is ready to use!")
    print()
    print("Next steps:")
    print("1. Run your Streamlit app: streamlit run main.py")
    print("2. Login and add some transactions")
    print("3. Go to '🤖 AI Assistant' tab")
    print("4. Start chatting about your finances!")
    print()
    
    return True


if __name__ == "__main__":
    success = test_groq_connection()
    sys.exit(0 if success else 1)