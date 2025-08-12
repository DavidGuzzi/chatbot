"""
Simple test script for the Modern Data Chatbot
Run this to test the chatbot with your tiendas_detalle.csv
"""

import os
import asyncio
from dotenv import load_dotenv
from modern_chatbot import ModernDataChatbot

# Load environment variables from .env file
load_dotenv()

async def test_chatbot():
    """Test the chatbot with sample questions"""
    
    print("🚀 Initializing Modern Data Chatbot...")
    
    # Initialize chatbot with .env configuration
    chatbot = ModernDataChatbot("tiendas_detalle.csv")
    
    # Show loaded configuration in debug mode
    if os.getenv('DEBUG', '').lower() == 'true':
        print(f"🔧 Loaded config from .env file")
    
    print("✅ Chatbot initialized successfully!\n")
    
    # Test questions in Spanish (matching your data context)
    test_questions = [
        "¿Cuál región tiene mejor performance en revenue?",
        "¿El experimento tuvo impacto positivo?", 
        "¿Qué tipo de tienda convierte mejor?",
        "Muéstrame las top 3 tiendas por conversion rate",
        "¿Hay diferencias entre Mall y Street stores?"
    ]
    
    print("🤖 Testing chatbot with sample questions...\n")
    
    for i, question in enumerate(test_questions, 1):
        print(f"{'='*60}")
        print(f"🔍 TEST {i}: {question}")
        print('='*60)
        
        try:
            # Ask the chatbot
            response = await chatbot.ask(question)
            
            # Display results
            print(f"💡 **ANSWER:** {response['answer']}\n")
            
            print(f"📊 **DATA (first 3 rows):**")
            for j, row in enumerate(response['data'][:3]):
                print(f"   {j+1}. {row}")
            
            if len(response['data']) > 3:
                print(f"   ... and {len(response['data']) - 3} more rows\n")
            
            print(f"🎯 **INSIGHTS:**")
            if response['insights']['recommendations']:
                for rec in response['insights']['recommendations']:
                    print(f"   • {rec}")
            else:
                print("   • No specific recommendations generated")
            
            print(f"\n⚡ **PERFORMANCE:**")
            print(f"   • SQL: {response['sql_used']}")
            print(f"   • Time: {response['execution_time']:.2f}s")
            print(f"   • Cached: {'Yes' if response['cached'] else 'No'}")
            print(f"   • Confidence: {response.get('confidence', 'N/A')}")
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
        
        print("\n" + "="*60 + "\n")
    
    # Show cache statistics
    cache_stats = chatbot.get_cache_stats()
    print("📈 **CACHE PERFORMANCE:**")
    print(f"   • Cached queries: {cache_stats['total_cached_queries']}")
    print(f"   • Cache hits: {cache_stats['total_cache_hits']}")
    print(f"   • Hit rate: {cache_stats['cache_hit_rate']:.1f}%")
    
    print("\n🎉 Testing completed!")
    
    # Interactive mode
    print("\n" + "="*60)
    print("🔄 INTERACTIVE MODE - Ask your own questions!")
    print("(Type 'quit' to exit)")
    print("="*60)
    
    while True:
        try:
            user_question = input("\n❓ Your question: ").strip()
            
            if user_question.lower() in ['quit', 'exit', 'salir']:
                print("👋 Goodbye!")
                break
            
            if not user_question:
                continue
                
            print(f"\n🤖 Processing: {user_question}")
            response = await chatbot.ask(user_question)
            
            print(f"\n💡 **Answer:** {response['answer']}")
            
            if response['data'] and not any('error' in str(row) for row in response['data'][:1]):
                print(f"\n📊 **Data sample:**")
                for i, row in enumerate(response['data'][:2]):
                    print(f"   {i+1}. {row}")
                
                if len(response['data']) > 2:
                    print(f"   ... (+{len(response['data']) - 2} more)")
            
            print(f"\n⚡ Time: {response['execution_time']:.2f}s | Cached: {'Yes' if response['cached'] else 'No'}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  WARNING: .env file not found!")
        print("   1. Copy .env.example to .env: cp .env.example .env")
        print("   2. Edit .env and add your OpenAI API key")
        print("   3. Run the script again\n")
        exit(1)
    
    # Check if OpenAI API key is configured
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  ERROR: OPENAI_API_KEY not configured in .env file")
        print("   Edit your .env file and set: OPENAI_API_KEY=your-api-key-here\n")
        exit(1)
    
    print("✅ Configuration loaded from .env file")
    
    # Run the test
    asyncio.run(test_chatbot())