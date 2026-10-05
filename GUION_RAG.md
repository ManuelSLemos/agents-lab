# Guion de clase: RAG avanzado con tools (base vectorial y markdown)

Archivo de trabajo: `rag_agent/agent.py` (en `adk web` aparece como **rag_agent**).

Idea para el alumno: **RAG es darle al agente información externa antes de que responda**. Hoy lo hacemos de dos formas, siempre con tools:

| Técnica | Para qué sirve | Cómo lo hace |
|---------|----------------|--------------|
| Base de datos vectorial | Buscar en muchos documentos por **significado** | Tool `buscar_cursos` |
| Markdown como contexto | Personalidad y **memoria** del agente | `perfil.md` en la instruction y tools `leer_memoria` / `guardar_memoria` |

Estructura:

```
rag_agent/
├── agent.py
├── perfil.md       # personalidad
├── memoria.md      # memoria (el agente escribe aquí)
└── cursos/         # un .md por curso: python.md, react.md, ia.md
```

---

## 0. Punto de partida (3 min)

Preguntar a la clase: ¿qué hacemos si Foxy tiene 500 cursos? No caben en la `instruction`.

> Solución: **buscar** solo los 2 o 3 documentos relevantes y dárselos al modelo. Eso es RAG (Retrieval-Augmented Generation).

## 1. Base de datos vectorial (12 min)

### La idea (sin matemáticas)

- Un **embedding** convierte un texto en una lista de números que representa su significado.
- Textos con significado parecido tienen números parecidos.
- Una **base vectorial** guarda esos números y encuentra los textos más cercanos a la pregunta.
- Resultado: "quiero hacer webs" encuentra el curso de React aunque no comparta ninguna palabra clave.

Usamos **ChromaDB** (base vectorial local, sin servidor) y **Ollama** con el modelo `nomic-embed-text` para crear los embeddings.

### Código para escribir en vivo

```python
import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

embeddings = OllamaEmbeddingFunction(url=OLLAMA, model_name="nomic-embed-text")
coleccion = chromadb.EphemeralClient().get_or_create_collection("cursos", embedding_function=embeddings)

archivos = sorted((AQUI / "cursos").glob("*.md"))
coleccion.upsert(ids=[a.stem for a in archivos], documents=[a.read_text() for a in archivos])
```

Explicar línea a línea:
- `EphemeralClient`: la base vive en memoria y se crea cada vez que arranca el agente.
- `upsert`: guarda cada `.md` con un id; ChromaDB calcula el embedding solo.

### La tool

```python
def buscar_cursos(pregunta: str) -> str:
    """Busca en el catálogo los cursos más parecidos a la pregunta del alumno."""
    resultado = coleccion.query(query_texts=[pregunta], n_results=2)
    return "\n\n".join(resultado["documents"][0])
```

```python
tools=[buscar_cursos],
```

Puntos a explicar:
- La base vectorial **no es** el agente: es una herramienta más. El agente decide cuándo buscar.
- `n_results=2`: devolvemos pocos documentos para no llenar el contexto.
- El docstring vuelve a ser lo que le dice al modelo cuándo usarla.

### Probar

- **"Quiero hacer páginas web, ¿qué curso me conviene y cuánto cuesta?"**
  Resultado esperado: llama a `buscar_cursos` y responde con React (180 €) y Python (120 €), con los datos de los `.md`.

Demo extra (buena para entender el significado): en un script o consola, buscar `"no sé programar"` y ver que devuelve primero **Python desde cero**, sin compartir palabras con el texto.

> Ojo: la búsqueda no es perfecta. Con "cómo funciona ChatGPT" el primer resultado fue React y la IA quedó segunda. Por eso devolvemos 2 resultados y dejamos que el modelo decida. Buen momento para hablar de calidad de los embeddings y del tamaño de los documentos.

## 2. Markdown como contexto: personalidad (5 min)

Idea: **un archivo de texto es la forma más simple de dar contexto**. Lo puede editar cualquiera sin tocar código.

`perfil.md`:

```markdown
# Personalidad de Foxy
- Te llamas Foxy y trabajas en la academia Ferrumox.
- Hablas siempre en español, con tono cercano y frases cortas.
- Terminas tus respuestas con una pregunta para seguir ayudando.
```

En el agente, leemos el archivo y lo metemos en la instruction:

```python
instruction = (AQUI / "perfil.md").read_text() + """
Ayudas a elegir cursos. Usa buscar_cursos para consultar el catálogo.
Al empezar usa leer_memoria. Si el alumno te cuenta algo sobre él, usa guardar_memoria.
"""
```

Demostración: cambiar una línea de `perfil.md` (por ejemplo "Hablas como un pirata"), reiniciar y ver que cambia el tono, sin tocar `agent.py`.

## 3. Markdown como memoria (8 min)

Idea: el agente **escribe** en un archivo, y en la siguiente conversación lo **lee**. Eso es memoria.

```python
def leer_memoria() -> str:
    """Lee lo que Foxy recuerda del alumno (nombre, intereses, nivel)."""
    return (AQUI / "memoria.md").read_text()


def guardar_memoria(dato: str) -> str:
    """Guarda un dato nuevo del alumno en la memoria. Ejemplo: 'Se llama Ana y quiere aprender Python'."""
    with open(AQUI / "memoria.md", "a") as f:
        f.write(f"- {dato}\n")
    return "Guardado."
```

```python
tools=[buscar_cursos, leer_memoria, guardar_memoria],
```

Puntos a explicar:
- Son dos funciones sencillas: leer el archivo y añadir una línea.
- El ejemplo en el docstring ayuda al modelo a saber **qué formato** guardar.
- Cada conversación empieza vacía; la memoria vive en el archivo, no en el modelo.

### Probar (en dos sesiones distintas)

1. **"Hola, me llamo Ana y soy principiante total"**
   Esperado: `leer_memoria`, luego `guardar_memoria` con "Se llama Ana y es principiante total".
2. Abrir **otra sesión** y preguntar **"¿Qué sabes de mí?"**
   Esperado: `leer_memoria` y responde "Recuerdo que eres Ana, principiante total".

Abrir `rag_agent/memoria.md` y enseñar a la clase que el dato está ahí.

## 4. Resumen (3 min)

```python
tools=[buscar_cursos, leer_memoria, guardar_memoria],
```

| Necesito... | Uso... |
|-------------|--------|
| Buscar en muchos documentos | Base vectorial + tool de búsqueda |
| Dar personalidad | Un `.md` dentro de la instruction |
| Dar memoria | Un `.md` + tools de leer y guardar |

Conexión con la clase anterior: son **tools** normales. Lo único nuevo es qué hace la función por dentro.

## Preguntas para la clase

- ¿Qué pasa si la memoria crece mucho? (Respuesta: no cabe en el contexto; habría que resumirla o guardarla también en la base vectorial.)
- ¿Qué problemas hay si varios alumnos comparten el mismo `memoria.md`? (Un archivo por alumno.)
- ¿Cómo mejorarías la búsqueda? (Dividir documentos en trozos, más resultados, filtrar por nivel.)

---

## Notas para el profesor

- Todo lo anterior se ensayó con `qwen3:4b` y `nomic-embed-text` en `adk web` y funcionó: búsqueda, guardado y lectura de memoria.
- Descargar el modelo de embeddings antes de la clase: `docker exec ollama ollama pull nomic-embed-text`.
- Dependencias nuevas (`chromadb`, `ollama`): reconstruir con `docker compose -p dice up -d --build adk`.
- **Restablecer `rag_agent/memoria.md`** a `# Memoria de Foxy` antes de empezar, para que la demo parta de cero.
- Para arrancar en local sin Docker: `OLLAMA_API_BASE=http://localhost:11434 uv run adk web`.
