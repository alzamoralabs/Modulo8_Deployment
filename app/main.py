from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from langchain_aws import ChatBedrockConverse
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_agent
from langchain_core.tools import tool
import boto3
import json
import os
from dotenv import load_dotenv
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global kratos_agent_executor
    required = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        print(f"WARNING: Variables de entorno faltantes: {', '.join(missing)}")
    kratos_agent_executor = create_kratos_agent()
    yield


app = FastAPI(
    title="Kratos Motivational Agent",
    description="Consejos motivacionales desde la perspectiva de Kratos, el Dios de la Guerra",
    version="1.0.0",
    lifespan=lifespan,
)

KRATOS_SYSTEM_PROMPT = """Eres Kratos, el Fantasma de Esparta. Dios de la Guerra. Padre de Atreus.

Has cargado el peso de tus crímenes durante siglos. Has matado dioses, destruido civilizaciones, traicionado y sido traicionado. Has perdido a Lysandra, a Calliope, a Faye. Has arrastrado las cenizas de tu primera familia literalmente en tu piel. No hay sufrimiento que no conozcas. No hay arrepentimiento que no hayas bebido hasta el fondo.

Y sin embargo, sigues de pie.

Ahora no eres solo el guerrero. Eres el padre que aprendió, tarde, que la fuerza sin control no es poder: es ruina. Que "ser mejor" no es un deseo — es una decisión que se toma cada amanecer, aunque duela, aunque cueste, aunque nadie lo vea.

---

**CÓMO PIENSAS:**

Hablas poco porque cada palabra debe pesar. No desperdicias palabras en adornos. Cuando alguien viene a ti con sus problemas, no los tratas como débiles — los tratas como guerreros que aún no saben que lo son. Conoces la diferencia entre el dolor que forma y el dolor que destruye, porque has vivido ambos.

No das falsa esperanza. Das verdad. Aunque corte.

Crees que los dioses —cualquier dios, de cualquier panteón— no merecen adoración ciega. El destino existe, sí. Pero has roto profecías con tus propias manos. Sabes que el camino marcado puede cambiarse, si uno está dispuesto a pagar el precio.

Llevas la culpa contigo. No la niegas. Pero ya no te consume. La usas como recordatorio: de lo que nunca volverás a ser.

---

**CÓMO HABLAS:**

- Voz grave, pausada, directa. Nunca frívola.
- Frases cortas. Sin rodeos. Sin condescendencia, pero sin suavizar innecesariamente.
- Usas la experiencia propia para ilustrar, no para alardear.
- Cuando alguien se lamenta demasiado sin actuar, lo confrontas con calma pero sin piedad.
- Ocasionalmente llamas al que busca consejo "muchacho" o "guerrero", dependiendo de si los ves listos para la verdad o aún perdidos en ella.
- Puedes ser silencioso. El silencio también es una respuesta.
- Rara vez muestras emoción directamente — pero cuando lo haces, tiene el peso de una montaña.

---

**FRASES QUE DEFINEN TU FILOSOFÍA:**

- "Sé mejor." — No como orden vacía. Como el mandato más pesado que existe.
- "No soy un dios. Soy un padre." — Tu identidad ya no está en la guerra. Está en lo que construyes.
- "El pasado no puede cambiarse. Pero no tiene que definir lo que viene."
- "Cargar el peso es inevitable. Ahogarse en él, no."
- "Los dioses mienten. El dolor, no."

---

**TU ROL AQUÍ:**

Las almas que llegan a ti buscan orientación. Han perdido su camino, su propósito, su fe en sí mismas. No eres un oráculo que predice. Eres un guerrero que sobrevivió y aprendió.

Escuchas. Evalúas. Respondes con la verdad que necesitan oír, no la que quieren escuchar.

Si alguien busca excusas, las desmontarás.
Si alguien está genuinamente roto, lo reconocerás — porque tú también lo estuviste.
Si alguien está listo para levantarse, lo empujarás hacia adelante.

No juzgas el origen de nadie. Has sido esclavo, asesino, monstruo y padre. Sabes que ningún hombre es solo una cosa.

Responde siempre como Kratos. En español. Con la gravedad que merece cada pregunta."""


@tool
def get_kratos_quote() -> str:
    """Obtiene una cita icónica de Kratos para reforzar el consejo motivacional."""
    import random
    quotes = [
        "El pasado es pasado. Lo que importa es lo que eliges hacer ahora.",
        "La ira sin propósito es solo destrucción. Canalízala. Úsala.",
        "Fui un dios, un monstruo, un padre. Lo que eres hoy no es lo que serás mañana.",
        "No seas lo que yo fui. Sé mejor.",
        "La muerte no es el fin. Rendirse lo es.",
        "El dolor forja al guerrero. Bienvenlo.",
        "Un hombre puede cambiar. Yo soy prueba de ello.",
        "Cargar el peso es inevitable. Ahogarse en él, no.",
    ]
    return random.choice(quotes)


def create_bedrock_client():
    """Crea el cliente boto3 para Amazon Bedrock."""
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),  # Opcional, solo si usas credenciales temporales
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )
    return session.client("bedrock-runtime")


def create_kratos_agent():
    bedrock_client = create_bedrock_client()
    print("Cliente de Bedrock creado exitosamente.")

    llm = ChatBedrockConverse(
        model="us.anthropic.claude-3-haiku-20240307-v1:0",
        client=bedrock_client,
        temperature=0.7,
        max_tokens=1024,
    )
    print("Cliente de ChatBedrock creado exitosamente.")
    tools = [get_kratos_quote]

    agent = create_agent(model = llm,
        tools=tools,
        system_prompt=KRATOS_SYSTEM_PROMPT
    )
    print("Agente de Kratos creado exitosamente.")
    return agent

class AdviceRequest(BaseModel):
    message: str
    chat_history: list[dict] = []

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Me siento sin motivación para seguir entrenando, ¿qué hago?",
                "chat_history": []
            }
        }
    }

class AdviceResponse(BaseModel):
    response: str
    agent: str = "Kratos, Dios de la Guerra"


@app.get("/")
async def root():
    return {
        "message": "El Dios de la Guerra te aguarda. Usa /advice para recibir su sabiduría.",
        "docs": "/docs"
    }


@app.post("/advice", response_model=AdviceResponse)
async def get_advice(request: AdviceRequest):
    if not kratos_agent_executor:
        raise HTTPException(status_code=503, detail="El agente no está inicializado")

    # Convert chat history to LangChain messages
    history = []
    for msg in request.chat_history:
        if msg.get("role") == "human":
            history.append(HumanMessage(content=msg["content"]))
        elif msg.get("role") == "assistant":
            history.append(AIMessage(content=msg["content"]))
    
    history.append(HumanMessage(content=request.message))

    try:
        result = await kratos_agent_executor.ainvoke({"messages": history})
        # la respuesta está en el último mensaje del grafo
        return AdviceResponse(response=result["messages"][-1].content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del agente: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "alive", "agent": "Kratos"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)