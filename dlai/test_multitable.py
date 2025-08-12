#!/usr/bin/env python3
"""
Test script para el chatbot con múltiples tablas relacionadas
"""

import os
import asyncio
from dotenv import load_dotenv
from modern_chatbot import ModernDataChatbot

# Load environment variables from .env file
load_dotenv()

async def test_multitable_chatbot():
    """Test the chatbot with multiple related tables"""
    
    print("🚀 Initializing Modern Data Chatbot with Multiple Tables...")
    
    # Initialize chatbot with both data and maestro tables
    chatbot = ModernDataChatbot("tiendas_detalle.csv", "maestro_tiendas.csv")
    
    print("✅ Chatbot initialized with both tables!\n")
    
    # Test questions that require JOIN operations
    test_questions = [
        "¿Cuáles son las tiendas con mejor performance? Muestra el nombre de la tienda",
        "¿Qué gerente maneja las tiendas con mayor revenue?",
        "Muéstrame las top 5 tiendas por conversion rate con sus nombres y gerentes",
        "¿Hay algún patrón entre el tipo de tienda y el nombre que se le asigna?",
        "¿Las tiendas abiertas en 2020 tienen mejor performance que las otras?",
        "Compara el performance entre Mall Norte vs Plaza Central"
    ]
    
    print("🤖 Testing chatbot with multi-table questions...\n")
    
    for i, question in enumerate(test_questions, 1):
        print(f"{'='*70}")
        print(f"🔍 TEST {i}: {question}")
        print('='*70)
        
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
            
            print(f"📝 **SQL USED:**")
            print(f"   {response['sql_used']}\n")
            
            print(f"🎯 **INSIGHTS:**")
            if response['insights']['recommendations']:
                for rec in response['insights']['recommendations']:
                    print(f"   • {rec}")
            else:
                print("   • No specific recommendations generated")
            
            print(f"\n⚡ **PERFORMANCE:**")
            print(f"   • Time: {response['execution_time']:.2f}s")
            print(f"   • Cached: {'Yes' if response['cached'] else 'No'}")
            print(f"   • Confidence: {response.get('confidence', 'N/A')}")
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
        
        print("\n" + "="*70 + "\n")
    
    # Show schema information
    print("📋 **DATABASE SCHEMA INFORMATION:**")
    schema = chatbot.schema_info
    print(f"Available tables: {list(schema['tables'].keys())}")
    for table_name, table_info in schema['tables'].items():
        print(f"  - {table_name}: {list(table_info['columns'].keys())}")
    
    print(f"\nRelationships: {schema.get('relationships', {})}")
    
    # Show cache statistics
    cache_stats = chatbot.get_cache_stats()
    print(f"\n📈 **CACHE PERFORMANCE:**")
    print(f"   • Cached queries: {cache_stats['total_cached_queries']}")
    print(f"   • Cache hits: {cache_stats['total_cache_hits']}")
    print(f"   • Hit rate: {cache_stats['cache_hit_rate']:.1f}%")
    
    print("\n🎉 Multi-table testing completed!")
    
    # Manual verification query
    print("\n🔧 **MANUAL VERIFICATION:**")
    print("Let's verify the JOIN is working correctly...")
    
    manual_response = await chatbot.ask("Muéstrame 3 tiendas con sus nombres completos")
    print(f"Manual query result: {manual_response['data'][:2]}")
    print(f"SQL used: {manual_response['sql_used']}")

if __name__ == "__main__":
    # Check if required files exist
    if not os.path.exists('tiendas_detalle.csv'):
        print("❌ ERROR: tiendas_detalle.csv not found!")
        exit(1)
    
    if not os.path.exists('maestro_tiendas.csv'):
        print("❌ ERROR: maestro_tiendas.csv not found!")
        print("   Run: python3 generate_maestro.py")
        exit(1)
    
    if not os.path.exists('.env'):
        print("⚠️  WARNING: .env file not found!")
        print("   1. Copy .env.example to .env: cp .env.example .env")
        print("   2. Edit .env and add your OpenAI API key")
        exit(1)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  ERROR: OPENAI_API_KEY not configured in .env file")
        exit(1)
    
    print("✅ All files and configuration ready")
    
    # Run the test
    asyncio.run(test_multitable_chatbot())