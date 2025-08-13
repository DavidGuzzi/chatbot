#!/usr/bin/env python3
"""
Test specific to the follow-up question issue
"""
import asyncio
from modern_chatbot import ModernDataChatbot

async def test_follow_up():
    print("🤖 Testing follow-up question handling...")
    chatbot = ModernDataChatbot("tiendas_detalle.csv", "maestro_tiendas.csv")
    
    session_id = "test_follow_up"
    
    # First question
    print("\n=== PRIMERA PREGUNTA ===")
    question1 = "¿Cuántos usuarios existen en todas las tiendas control?"
    response1 = await chatbot.ask(question1, session_id=session_id)
    print(f"❓ Pregunta: {question1}")
    print(f"✅ Respuesta: {response1['answer'][:200]}...")
    print(f"📊 SQL: {response1['sql_used']}")
    
    # Follow-up question that should fail logically
    print("\n=== SEGUNDA PREGUNTA (FOLLOW-UP) ===")
    question2 = "¿Qué tipo de tienda te mencioné anteriormente?"
    response2 = await chatbot.ask(question2, session_id=session_id)
    print(f"❓ Pregunta: {question2}")
    print(f"✅ Respuesta: {response2['answer']}")
    print(f"📊 SQL: {response2['sql_used']}")
    print(f"🚀 SQL Ejecutado: {'Sí' if response2['sql_executed'] else 'No'}")
    print(f"🔍 Reasoning: {response2['reasoning']}")
    
    # Show conversation history
    print("\n=== HISTORIAL DE CONVERSACIÓN ===")
    history = chatbot.get_session_history(session_id)
    for i, turn in enumerate(history, 1):
        print(f"{i}. P: {turn['question']}")
        print(f"   R: {turn['answer'][:100]}...")
        print()

if __name__ == "__main__":
    asyncio.run(test_follow_up())