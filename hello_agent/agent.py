from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.skills import load_skill_from_dir
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from google.adk.tools.skill_toolset import SkillToolset
from mcp import StdioServerParameters
from pathlib import Path


# 1. TOOL: una función de Python normal. El docstring le explica al modelo cuándo usarla.
def listar_cursos() -> list[str]:
    """Devuelve los cursos que ofrece la academia Ferrumox."""
    return ["Python desde cero", "React para principiantes", "Introducción a la IA"]


# 2. SKILL: instrucciones en un archivo SKILL.md que el agente carga solo cuando las necesita.
elegir_curso = load_skill_from_dir(Path(__file__).parent / "skills" / "elegir-curso")

# 3. MCP: un servidor externo que le da herramientas al agente (aquí, la hora actual).
mcp_hora = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(command="uvx", args=["mcp-server-time"])
    )
)


root_agent = Agent(
    name="hello_agent",
    model=LiteLlm(model="ollama_chat/qwen3:4b"),
    description="A simple agent that greets the user.",
    instruction="Eres un experto asistente en la academia de Ferrumox. Tu nombre es Foxy. Ayudaras a los alumnos a elegir entre las diferentes opciones de cursos y carreras que ofrece la academia. Tu objetivo es guiar a los alumnos en su proceso de aprendizaje y brindarles información útil sobre los cursos disponibles.",
    tools=[listar_cursos, SkillToolset(skills=[elegir_curso]), mcp_hora],
)
