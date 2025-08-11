import openai
import pandas as pd
import json
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
import numpy as np

class ChatbotCSV:
    """
    Chatbot para análisis de archivos CSV usando OpenAI GPT-4
    con function calling para ejecución segura de código pandas.
    """
    
    def __init__(self, csv_path: str, api_key: str, model: str = "gpt-4-turbo-preview"):
        """
        Inicializa el chatbot con un archivo CSV.
        
        Args:
            csv_path: Ruta al archivo CSV
            api_key: API key de OpenAI
            model: Modelo de OpenAI a usar
        """
        openai.api_key = api_key
        self.model = model
        self.df = pd.read_csv(csv_path)
        self.csv_path = csv_path
        self.historial = []
        
        # Generar metadata del dataset
        self.metadata = self._generar_metadata()
        
        # Definir las funciones disponibles para OpenAI
        self.functions = [
            {
                "name": "ejecutar_consulta_pandas",
                "description": "Ejecuta código pandas para analizar el dataset CSV",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "codigo": {
                            "type": "string",
                            "description": "Código pandas para ejecutar. El dataframe está disponible como 'df'"
                        },
                        "explicacion": {
                            "type": "string",
                            "description": "Breve explicación de lo que hace el código"
                        }
                    },
                    "required": ["codigo", "explicacion"]
                }
            },
            {
                "name": "obtener_info_dataset",
                "description": "Obtiene información general sobre el dataset",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tipo_info": {
                            "type": "string",
                            "enum": ["columnas", "tipos", "estadisticas", "muestra", "dimensiones"],
                            "description": "Tipo de información a obtener"
                        }
                    },
                    "required": ["tipo_info"]
                }
            }
        ]
    
    def _generar_metadata(self) -> Dict[str, Any]:
        """Genera metadata del dataset para contexto."""
        return {
            "columnas": self.df.columns.tolist(),
            "filas": len(self.df),
            "tipos_datos": self.df.dtypes.astype(str).to_dict(),
            "valores_nulos": self.df.isnull().sum().to_dict(),
            "columnas_numericas": self.df.select_dtypes(include=[np.number]).columns.tolist(),
            "columnas_texto": self.df.select_dtypes(include=['object']).columns.tolist()
        }
    
    def _ejecutar_codigo_seguro(self, codigo: str) -> Dict[str, Any]:
        """
        Ejecuta código pandas de forma segura con validaciones.
        
        Args:
            codigo: Código pandas a ejecutar
            
        Returns:
            Dict con resultado y estado de ejecución
        """
        # Limpieza básica del código
        codigo = codigo.strip()
        
        # Validaciones de seguridad básicas
        palabras_prohibidas = ['import os', 'import sys', '__import__', 'exec', 
                               'eval', 'open(', 'file(', 'input(', 'raw_input']
        
        for palabra in palabras_prohibidas:
            if palabra in codigo.lower():
                return {
                    "exito": False,
                    "error": f"Código contiene operación no permitida: {palabra}",
                    "resultado": None
                }
        
        # Namespace limitado para ejecución
        namespace = {
            'df': self.df.copy(),  # Usar copia para evitar modificaciones
            'pd': pd,
            'np': np,
            'datetime': datetime
        }
        
        try:
            # Ejecutar el código
            resultado = eval(codigo, {"__builtins__": {}}, namespace)
            
            # Formatear resultado según tipo
            if isinstance(resultado, pd.DataFrame):
                if len(resultado) > 100:
                    resultado_str = f"DataFrame con {len(resultado)} filas y {len(resultado.columns)} columnas\n"
                    resultado_str += f"Primeras 10 filas:\n{resultado.head(10).to_string()}"
                else:
                    resultado_str = resultado.to_string()
            elif isinstance(resultado, pd.Series):
                if len(resultado) > 50:
                    resultado_str = f"Series con {len(resultado)} elementos\n"
                    resultado_str += f"Primeros 10 elementos:\n{resultado.head(10).to_string()}"
                else:
                    resultado_str = resultado.to_string()
            else:
                resultado_str = str(resultado)
            
            return {
                "exito": True,
                "resultado": resultado_str,
                "tipo_resultado": type(resultado).__name__
            }
            
        except Exception as e:
            return {
                "exito": False,
                "error": str(e),
                "resultado": None
            }
    
    def obtener_info_dataset(self, tipo_info: str) -> str:
        """
        Obtiene información específica del dataset.
        
        Args:
            tipo_info: Tipo de información solicitada
            
        Returns:
            String con la información solicitada
        """
        if tipo_info == "columnas":
            return f"Columnas del dataset: {', '.join(self.metadata['columnas'])}"
        
        elif tipo_info == "tipos":
            tipos_str = "\n".join([f"- {col}: {tipo}" for col, tipo in self.metadata['tipos_datos'].items()])
            return f"Tipos de datos:\n{tipos_str}"
        
        elif tipo_info == "estadisticas":
            return self.df.describe().to_string()
        
        elif tipo_info == "muestra":
            return f"Primeras 5 filas del dataset:\n{self.df.head().to_string()}"
        
        elif tipo_info == "dimensiones":
            return f"El dataset tiene {self.metadata['filas']} filas y {len(self.metadata['columnas'])} columnas"
        
        else:
            return "Tipo de información no reconocido"
    
    def _crear_prompt_sistema(self) -> str:
        """Crea el prompt del sistema con contexto del dataset."""
        return f"""Eres un analista de datos experto que ayuda a analizar un dataset CSV.
        
INFORMACIÓN DEL DATASET:
- Archivo: {self.csv_path}
- Dimensiones: {self.metadata['filas']} filas x {len(self.metadata['columnas'])} columnas
- Columnas: {', '.join(self.metadata['columnas'])}
- Columnas numéricas: {', '.join(self.metadata['columnas_numericas'])}
- Columnas de texto: {', '.join(self.metadata['columnas_texto'])}

INSTRUCCIONES:
1. Usa la función 'ejecutar_consulta_pandas' para analizar los datos
2. El dataframe está disponible como 'df'
3. Siempre explica qué estás haciendo antes de ejecutar código
4. Si hay errores, intenta corregirlos y ejecutar de nuevo
5. Proporciona respuestas claras y concisas
6. Para consultas complejas, divide el problema en pasos

IMPORTANTE: 
- NO modifiques el dataframe original (usa .copy() si necesitas modificar)
- Verifica los nombres de columnas exactos antes de usarlos
- Considera valores nulos en tus análisis"""
    
    def procesar_pregunta(self, pregunta: str, usar_historial: bool = True) -> str:
        """
        Procesa una pregunta del usuario sobre el dataset.
        
        Args:
            pregunta: Pregunta del usuario
            usar_historial: Si usar el historial de conversación
            
        Returns:
            Respuesta generada por el modelo
        """
        # Preparar mensajes
        mensajes = [
            {"role": "system", "content": self._crear_prompt_sistema()}
        ]
        
        # Agregar historial si corresponde
        if usar_historial and self.historial:
            mensajes.extend(self.historial[-10:])  # Últimos 10 mensajes
        
        # Agregar pregunta actual
        mensajes.append({"role": "user", "content": pregunta})
        
        try:
            # Llamada inicial a OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=mensajes,
                functions=self.functions,
                function_call="auto",
                temperature=0.1  # Baja temperatura para respuestas más consistentes
            )
            
            message = response.choices[0].message
            
            # Si el modelo quiere ejecutar una función
            if message.get("function_call"):
                function_name = message["function_call"]["name"]
                function_args = json.loads(message["function_call"]["arguments"])
                
                # Ejecutar la función correspondiente
                if function_name == "ejecutar_consulta_pandas":
                    resultado = self._ejecutar_codigo_seguro(function_args["codigo"])
                    
                    # Preparar respuesta de la función
                    if resultado["exito"]:
                        function_response = f"Resultado exitoso:\n{resultado['resultado']}"
                    else:
                        function_response = f"Error al ejecutar código: {resultado['error']}"
                    
                    # Agregar explicación del código
                    function_response = f"Explicación: {function_args['explicacion']}\n\n{function_response}"
                
                elif function_name == "obtener_info_dataset":
                    function_response = self.obtener_info_dataset(function_args["tipo_info"])
                
                # Obtener respuesta final del modelo
                mensajes.append(message)
                mensajes.append({
                    "role": "function",
                    "name": function_name,
                    "content": function_response
                })
                
                final_response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=mensajes,
                    temperature=0.1
                )
                
                respuesta_final = final_response.choices[0].message["content"]
                
            else:
                # Respuesta directa sin función
                respuesta_final = message["content"]
            
            # Actualizar historial
            if usar_historial:
                self.historial.append({"role": "user", "content": pregunta})
                self.historial.append({"role": "assistant", "content": respuesta_final})
            
            return respuesta_final
            
        except Exception as e:
            return f"Error al procesar la pregunta: {str(e)}"
    
    def limpiar_historial(self):
        """Limpia el historial de conversación."""
        self.historial = []
        print("Historial limpiado.")
    
    def guardar_sesion(self, archivo: str):
        """
        Guarda la sesión actual (historial) en un archivo JSON.
        
        Args:
            archivo: Ruta del archivo donde guardar la sesión
        """
        sesion = {
            "timestamp": datetime.now().isoformat(),
            "csv_path": self.csv_path,
            "historial": self.historial,
            "metadata": self.metadata
        }
        
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(sesion, f, ensure_ascii=False, indent=2)
        
        print(f"Sesión guardada en {archivo}")
    
    def cargar_sesion(self, archivo: str):
        """
        Carga una sesión guardada previamente.
        
        Args:
            archivo: Ruta del archivo de sesión
        """
        with open(archivo, 'r', encoding='utf-8') as f:
            sesion = json.load(f)
        
        self.historial = sesion["historial"]
        print(f"Sesión cargada: {len(self.historial)} mensajes en historial")


# ============= EJEMPLO DE USO =============

def main():
    """Ejemplo de uso del chatbot."""
    
    # Crear un CSV de ejemplo para demostración
    print("Creando dataset de ejemplo...")
    
    data = {
        'tienda_id': range(1, 101),
        'tipo_tienda': ['control'] * 50 + ['test'] * 50,
        'usuarios': np.random.randint(100, 1000, 100),
        'ventas': np.random.uniform(10000, 100000, 100),
        'region': np.random.choice(['Norte', 'Sur', 'Este', 'Oeste'], 100),
        'satisfaccion': np.random.uniform(3.0, 5.0, 100)
    }
    
    df_ejemplo = pd.DataFrame(data)
    df_ejemplo.to_csv('tiendas_ejemplo.csv', index=False)
    print("Dataset 'tiendas_ejemplo.csv' creado!\n")
    
    # Inicializar chatbot
    API_KEY = "tu-api-key-aqui"  # Reemplazar con tu API key
    chatbot = ChatbotCSV('tiendas_ejemplo.csv', API_KEY)
    
    # Ejemplos de preguntas
    preguntas_ejemplo = [
        "¿Cuántas tiendas hay en total?",
        "¿Cuántos usuarios totales hay en tiendas control?",
        "¿Cuál es el promedio de ventas por tipo de tienda?",
        "¿Qué región tiene la mayor satisfacción promedio?",
        "Muéstrame las 5 tiendas con más usuarios",
        "¿Hay correlación entre usuarios y ventas?",
        "Crea un resumen estadístico por tipo de tienda"
    ]
    
    print("=" * 50)
    print("DEMOSTRACIÓN DEL CHATBOT CSV")
    print("=" * 50)
    
    for pregunta in preguntas_ejemplo[:3]:  # Ejecutar solo 3 para demo
        print(f"\n📊 PREGUNTA: {pregunta}")
        print("-" * 40)
        respuesta = chatbot.procesar_pregunta(pregunta)
        print(f"💬 RESPUESTA:\n{respuesta}")
        print("=" * 50)
        
        # Simular pausa entre preguntas
        import time
        time.sleep(1)


# Función auxiliar para uso interactivo
def iniciar_chat_interactivo(csv_path: str, api_key: str):
    """
    Inicia una sesión interactiva del chatbot.
    
    Args:
        csv_path: Ruta al archivo CSV
        api_key: API key de OpenAI
    """
    chatbot = ChatbotCSV(csv_path, api_key)
    
    print("\n🤖 Chatbot CSV iniciado!")
    print("Escribe 'salir' para terminar, 'limpiar' para limpiar historial")
    print("=" * 50)
    
    while True:
        pregunta = input("\n👤 Tu pregunta: ")
        
        if pregunta.lower() == 'salir':
            print("¡Hasta luego!")
            break
        elif pregunta.lower() == 'limpiar':
            chatbot.limpiar_historial()
            continue
        
        print("\n🔄 Procesando...")
        respuesta = chatbot.procesar_pregunta(pregunta)
        print(f"\n🤖 Respuesta:\n{respuesta}")


if __name__ == "__main__":
    # Ejecutar demostración
    # main()
    
    # Para uso real:
    # iniciar_chat_interactivo('tu_archivo.csv', 'tu-api-key')
    pass

"""
# 1. Instalación de dependencias
pip install openai pandas numpy

# 2. Uso básico
from chatbot_csv import ChatbotCSV

# Inicializar con tu CSV y API key
chatbot = ChatbotCSV(
    csv_path='tu_archivo.csv',
    api_key='tu-api-key-de-openai'
)

# Hacer preguntas
respuesta = chatbot.procesar_pregunta("¿Cuántos usuarios hay en tiendas control?")
print(respuesta)

# 3. Modo interactivo
iniciar_chat_interactivo('tu_archivo.csv', 'tu-api-key')
"""