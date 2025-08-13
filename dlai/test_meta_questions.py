#!/usr/bin/env python3
"""
Test meta-questions that shouldn't require SQL execution
"""
import asyncio
from modern_chatbot import ModernDataChatbot

async def test_meta_questions():
    print("🤖 Testing meta-questions that shouldn't execute SQL...")
    chatbot = ModernDataChatbot("tiendas_detalle.csv", "maestro_tiendas.csv")
    
    session_id = "test_meta"
    
    # First establish some context
    print("\n=== ESTABLECIENDO CONTEXTO ===")
    context_questions = [
        "¿Cuántos usuarios hay en total?",
        "¿Cuál es el revenue promedio por tienda?"
    ]
    
    for question in context_questions:
        response = await chatbot.ask(question, session_id=session_id)
        print(f"❓ {question}")
        print(f"✅ SQL ejecutado: {'Sí' if response['sql_executed'] else 'No'}")
        print(f"📊 SQL: {response['sql_used'][:60]}...")
        print()
    
    # Now test meta-questions
    print("=== PREGUNTAS META (NO DEBERÍAN EJECUTAR SQL) ===")
    meta_questions = [
        "¿Qué me preguntaste primero?",
        "¿Cuántas preguntas me has hecho?",
        "¿Sobre qué temas hemos conversado?",
        "Explícame el resultado anterior",
        "¿Qué tipo de tienda te mencioné anteriormente?"  # Follow-up sin contexto
    ]
    
    for question in meta_questions:
        response = await chatbot.ask(question, session_id=session_id)
        print(f"❓ {question}")
        print(f"✅ Respuesta: {response['answer'][:100]}...")
        print(f"🚀 SQL Ejecutado: {'Sí' if response['sql_executed'] else 'No'}")
        print(f"📊 SQL: {response['sql_used']}")
        print(f"🔍 Confidence: {response['confidence']}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_meta_questions())