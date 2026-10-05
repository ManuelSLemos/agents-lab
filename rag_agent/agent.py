from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
import os

AQUI = Path(__file__).parent
OLLAMA = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")

# 1. BASE DE DATOS VECTORIAL: guardamos cada .md como un vector (embedding).
embeddings = OllamaEmbeddingFunction(url=OLLAMA, model_name="nomic-embed-text")
coleccion = chromadb.EphemeralClient().get_or_create_collection("cursos", embedding_function=embeddings)
archivos = sorted((AQUI / "cursos").glob("*.md"))
coleccion.upsert(ids=[a.stem for a in archivos], documents=[a.read_text() for a in archivos])


def buscar_cursos(pregunta: str) -> str:
    """Busca en el catálogo los cursos más parecidos a la pregunta del alumno."""
    resultado = coleccion.query(query_texts=[pregunta], n_results=2)
    return "\n\n".join(resultado["documents"][0])


# 2. MD COMO MEMORIA: el agente lee y escribe un archivo de texto.
def leer_memoria() -> str:
    """Lee lo que Foxy recuerda del alumno (nombre, intereses, nivel)."""
    return (AQUI / "memoria.md").read_text()


def guardar_memoria(dato: str) -> str:
    """Guarda un dato nuevo del alumno en la memoria. Ejemplo: 'Se llama Ana y quiere aprender Python'."""
    with open(AQUI / "memoria.md", "a") as f:
        f.write(f"- {dato}\n")
    return "Guardado."


# 3. MD COMO PERSONALIDAD: el contenido de perfil.md se mete en la instruction.
instruction = (AQUI / "perfil.md").read_text() + """
Ayudas a elegir cursos. Usa buscar_cursos para consultar el catálogo.
Al empezar usa leer_memoria. Si el alumno te cuenta algo sobre él, usa guardar_memoria.
"""

root_agent = Agent(
    name="rag_agent",
    model=LiteLlm(model="ollama_chat/qwen3:4b"),
    description="Foxy con búsqueda vectorial y memoria en markdown.",
    instruction=instruction,
    tools=[buscar_cursos, leer_memoria, guardar_memoria],
)
