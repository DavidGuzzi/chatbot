#!/usr/bin/env python3
"""
Interactive test for the enhanced chatbot with session memory
"""
import asyncio
from modern_chatbot import ModernDataChatbot

async def interactive_chat():
    print("🤖 Inicializando chatbot con memoria de sesión...")
    chatbot = ModernDataChatbot("tiendas_detalle.csv", "maestro_tiendas.csv")
    
    session_id = "interactive_session"
    print(f"📋 Sesión iniciada: {session_id}")
    print("💡 Prueba preguntas de seguimiento como '¿y cuál región tiene mejor conversión?'")
    print("✋ Escribe 'salir' para terminar\n")
    
    while True:
        try:
            question = input("❓ Tu pregunta: ").strip()
            
            if question.lower() in ['salir', 'exit', 'quit']:
                break
                
            if not question:
                continue
                
            print("🤔 Procesando...")
            response = await chatbot.ask(question, session_id=session_id)
            
            print(f"\n✅ **Respuesta:** {response['answer']}")
            print(f"📊 **SQL:** {response['sql_used']}")
            print(f"⚡ **Tiempo:** {response['execution_time']:.2f}s")
            print(f"💾 **Cached:** {'Sí' if response['cached'] else 'No'}")
            
            if response['insights']['recommendations']:
                print("💡 **Recomendaciones:**")
                for rec in response['insights']['recommendations'][:2]:
                    print(f"   - {rec}")
            
            print("-" * 60, "\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    # Show session stats
    stats = chatbot.get_session_stats()
    print(f"\n📈 **Estadísticas de la sesión:**")
    print(f"   - Turnos de conversación: {stats['total_conversation_turns']}")
    print(f"   - Sesiones activas: {stats['active_sessions']}")
    
    print("👋 ¡Hasta luego!")

if __name__ == "__main__":
    asyncio.run(interactive_chat())