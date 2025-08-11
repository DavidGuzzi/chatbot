import pandas as pd
from openai import OpenAI
import ast

# 1. Cargar CSV
df = pd.read_csv("tiendas_detalle.csv")

# 2. Crear un resumen del DataFrame para darle contexto al LLM
#    (evitamos pasar todas las filas, solo columnas y valores únicos)
schema_info = []
for col in df.columns:
    unique_vals = df[col].dropna().unique()
    unique_preview = unique_vals[:10]  # primeros 10 valores
    schema_info.append(f"{col} ({df[col].dtype}): valores ejemplo: {list(unique_preview)}")

schema_text = "\n".join(schema_info)

# 3. Inicializar cliente OpenAI
client = OpenAI(api_key="TU_API_KEY")

# 4. Pregunta del usuario
user_question = "¿Cuántos usuarios totales hay en tiendas control?"

# 5. Pedir al LLM que genere código Pandas
system_prompt = f"""
Eres un asistente que traduce preguntas en español a código Python con Pandas.
Debes usar el DataFrame `df` que ya está cargado.
Responde únicamente con código Python válido que realice el cálculo.
DataFrame info:
{schema_text}
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",  # o el modelo que uses
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ],
    max_tokens=300,
    temperature=0
)

# 6. Extraer el código generado
code_str = response.choices[0].message.content.strip("```python").strip("```").strip()

print("Código generado:\n", code_str)

# 7. Ejecutar de forma segura (solo eval expresiones o exec controlado)
#    Aquí usamos exec, pero podrías usar 'restricted execution'
local_vars = {"df": df}
exec(code_str, {}, local_vars)

# Si el código genera una variable 'resultado', la mostramos
if "resultado" in local_vars:
    print("Resultado:", local_vars["resultado"])
