# Guion de clase: Tools, Skills y MCP en un agente

Archivo de trabajo: `hello_agent/agent.py`. Partimos del agente Foxy, que solo tiene `instruction`.

Idea para el alumno: **al agente le damos tres formas de ampliar lo que sabe hacer**.

| Concepto | Qué es | Dónde vive |
|----------|--------|-----------|
| Tool | Una función Python que el agente puede llamar | En nuestro código |
| Skill | Instrucciones en un archivo que el agente lee cuando las necesita | Un `SKILL.md` |
| MCP | Herramientas que ofrece un servidor externo | Otro programa |

---

## 0. Punto de partida (2 min)

Mostrar el agente actual y arrancar `adk web` (http://localhost:8000). Preguntar "¿qué cursos hay?".

> Foxy no tiene acceso a datos reales, así que solo puede improvisar. Vamos a darle herramientas.

## 1. Tool (5 min)

Escribir en vivo:

```python
def listar_cursos() -> list[str]:
    """Devuelve los cursos que ofrece la academia Ferrumox."""
    return ["Python desde cero", "React para principiantes", "Introducción a la IA"]
```

Y en el agente:

```python
tools=[listar_cursos],
```

Puntos a explicar:
- Es una función normal, sin nada especial.
- **El docstring es clave**: el modelo lo lee para decidir cuándo llamarla.
- Los tipos (`-> list[str]`) también le ayudan.

Probar: **"¿Qué cursos hay en la academia?"**

Resultado esperado: llama a `listar_cursos` y responde con los 3 cursos. En `adk web` se ve la llamada a la tool en la traza.

## 2. Skill (7 min)

Crear `hello_agent/skills/elegir-curso/SKILL.md`:

```markdown
---
name: elegir-curso
description: Guía para recomendar un curso a un alumno según su nivel y objetivo.
---

# Cómo recomendar un curso

1. Pregunta al alumno cuál es su nivel (principiante, intermedio o avanzado).
2. Pregunta cuál es su objetivo (web, datos o IA).
3. Usa la herramienta `listar_cursos` y elige el curso que mejor encaje.
4. Responde con el nombre del curso y una frase explicando por qué.
```

Cargarla en el agente:

```python
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from pathlib import Path

elegir_curso = load_skill_from_dir(Path(__file__).parent / "skills" / "elegir-curso")

tools=[listar_cursos, SkillToolset(skills=[elegir_curso])],
```

Puntos a explicar:
- Una tool **hace** algo. Una skill **enseña cómo hacer** algo.
- El agente solo ve el `name` y la `description`. Lee el contenido completo únicamente cuando decide usarla, así no gasta contexto.
- Nuestra skill usa la tool `listar_cursos`: se pueden combinar.

Probar: **"Quiero elegir un curso, usa la skill elegir-curso"**

Resultado esperado: llama a `load_skill` con `elegir-curso` y pregunta el nivel y el objetivo del alumno. En la traza se ve `load_skill`.

> Ojo: con "Ayúdame a elegir un curso" (sin nombrar la skill) el modelo no la carga y solo lista los cursos. Es buen momento para explicar que **la description decide cuándo se usa una skill**: se puede mejorar y volver a probar.

## 3. MCP (7 min)

Explicar primero con una frase: **MCP es un estándar para que cualquier programa ofrezca herramientas a un agente**, sin que tengamos que escribirlas nosotros.

Usamos `mcp-server-time`, un servidor oficial que da la hora. No necesita cuenta ni API key.

```python
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

mcp_hora = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(command="uvx", args=["mcp-server-time"])
    )
)

tools=[listar_cursos, SkillToolset(skills=[elegir_curso]), mcp_hora],
```

Puntos a explicar:
- `uvx mcp-server-time` arranca el servidor como un proceso aparte. ADK se comunica con él por stdin/stdout.
- No escribimos ninguna función: el servidor dice qué herramientas tiene (`get_current_time`, `convert_time`) y ADK las añade solo.
- Requiere el paquete `mcp` (`uv add mcp`).

Probar:
- **"¿Qué hora es en Madrid ahora mismo?"**: llama a `get_current_time` con `Europe/Madrid` y da la hora real.
- **"Si son las 10:00 en Madrid, ¿qué hora es en Ciudad de México?"**: llama a `convert_time` y responde las 2:00 a.m. (8 horas de diferencia).

## 4. Resumen (2 min)

```python
tools=[listar_cursos, SkillToolset(skills=[elegir_curso]), mcp_hora],
```

Una línea, tres formas de ampliar al agente:
- **Tool**: lo escribo yo en Python.
- **Skill**: le doy instrucciones en un archivo.
- **MCP**: conecto herramientas de otro programa.

## Pregunta final para los alumnos

> ¿Qué tool, skill o MCP le añadirías a Foxy para que fuera más útil en la academia?

---

## Notas para el profesor

- Todas las pruebas de arriba se ensayaron con `qwen3:4b` en `adk web` y funcionaron.
- Arranque: `docker compose -p dice up -d`. Si cambias dependencias, reconstruir con `docker compose -p dice up -d --build adk`. (El `-p dice` es necesario porque los contenedores existentes pertenecen a ese proyecto.)
- Modelo: `qwen3:4b` en Ollama. Es pequeño y a veces no elige la tool o la skill. Si pasa, repetir la pregunta o nombrar la skill ("usa la skill elegir-curso").
- Si `adk web` no encuentra el MCP, comprobar que `uvx` está en el PATH.
- La primera ejecución de `uvx mcp-server-time` descarga el paquete y tarda unos segundos.
