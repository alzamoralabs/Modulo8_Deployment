# Modulo8_LLMOps_Deployment
# ⚔️ Kratos Motivational Agent — Backend

Agente conversacional motivacional construido con **LangChain + LangGraph**, expuesto como API REST con **FastAPI** y desplegado en contenedores Docker. El agente responde desde la personalidad de **Kratos, el Dios de la Guerra**, dando consejos de vida con la gravedad y filosofía del personaje.

> Este repositorio es el **backend**. El frontend vive en [Modulo8_Deployment_Front](https://github.com/alzamoralabs/Modulo8_Deployment_Front).

---

## 🏗️ Arquitectura

```
┌──────────────────────────────────────────┐      HTTP      ┌──────────────────────────┐
│   Modulo8_Deployment_Front               │ ────────────► │   Modulo8_Deployment     │
│   Streamlit :8501                        │               │   FastAPI :8000           │
│   github.com/alzamoralabs/               │               │   LangGraph Agent         │
│   Modulo8_Deployment_Front               │               │   Amazon Bedrock          │
└──────────────────────────────────────────┘               │   Claude Haiku 3.5        │
                                                           └──────────────────────────┘
```

---

## 📁 Estructura del proyecto

```
Modulo8_Deployment/
├── app/
│   └── main.py              # FastAPI + LangGraph agent
├── Dockerfile               # Imagen del backend
├── docker-compose.yml       # Orquestación local
├── requirements.txt         # Dependencias Python
├── kratos.prompt.txt        # System prompt de Kratos
└── README.md
```

---

## 🤖 Stack tecnológico

| Componente | Tecnología |
|---|---|
| API | FastAPI |
| Agent framework | LangChain + LangGraph |
| LLM | Claude Haiku 3.5 vía Amazon Bedrock |
| AWS SDK | boto3 |
| Containerización | Docker |
| Orquestación | Docker Compose |

---

## ⚙️ Requisitos previos

- Docker Desktop instalado y corriendo
- Cuenta AWS con acceso a **Amazon Bedrock**
- Modelo **Claude Haiku 3.5** habilitado en Bedrock → Model access
- Credenciales IAM con permiso `bedrock:InvokeModel`

---

## 🚀 Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/alzamoralabs/Modulo8_Deployment.git
cd Modulo8_Deployment
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el `.env` con tus credenciales:

```env
AWS_ACCESS_KEY_ID=tu-access-key
AWS_SECRET_ACCESS_KEY=tu-secret-key
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-haiku-3-5-20241022-v1:0
```

### 3. Levantar con Docker

```bash
docker compose up --build
```

### 4. Verificar que está corriendo

```bash
curl http://localhost:8000/health
```

---

## 📡 Endpoints de la API

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Bienvenida |
| `POST` | `/advice` | Solicitar consejo motivacional |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI interactivo |

### Ejemplo de request

```bash
curl -X POST http://localhost:8000/advice \
  -H "Content-Type: application/json" \
  -d '{"message": "No tengo fuerzas para seguir con mi proyecto"}'
```

### Ejemplo de respuesta

```json
{
  "response": "Muchacho. El cansancio no es el enemigo. La rendición sí lo es...",
  "agent": "Kratos, Dios de la Guerra"
}
```

### Request con historial de conversación

```json
{
  "message": "¿Cómo superaste perder a tu familia?",
  "chat_history": [
    {"role": "user", "content": "Hola Kratos"},
    {"role": "assistant", "content": "Habla. ¿Qué te trae ante mí?"}
  ]
}
```

---

## 🧠 El agente

El agente usa `create_react_agent` de LangGraph con:

- **System prompt** definido en `kratos.prompt.txt` — personalidad, filosofía, tono y rol de Kratos
- **Tool `get_kratos_quote`** — el agente puede invocarla para reforzar sus consejos con citas icónicas del personaje
- **Amazon Bedrock** como proveedor LLM vía `ChatBedrockConverse` de `langchain-aws`

---

## 🔐 Seguridad

- Las credenciales AWS **nunca se hardcodean** en el código — se leen desde variables de entorno
- El `.env` está en `.gitignore` — nunca subir credenciales al repositorio
- Si expones credenciales accidentalmente: rotarlas de inmediato en **IAM → Security credentials**

---

## 🔧 Desarrollo local (sin Docker)

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cd app
python main.py
```

La API queda disponible en `http://127.0.0.1:8000`.

---

## 📦 Variables de entorno

| Variable | Requerida | Descripción |
|---|---|---|
| `AWS_ACCESS_KEY_ID` | ✅ | AWS Access Key |
| `AWS_SECRET_ACCESS_KEY` | ✅ | AWS Secret Key |
| `AWS_REGION` | ✅ | Región AWS (default: `us-east-1`) |
| `BEDROCK_MODEL_ID` | ✅ | ID del inference profile de Bedrock |
| `AWS_SESSION_TOKEN` | ❌ | Solo para credenciales temporales (SSO/STS) |

---

## 🔗 Repositorios relacionados

| Repo | Descripción |
|---|---|
| [Modulo8_Deployment](https://github.com/alzamoralabs/Modulo8_Deployment) | Backend — Este repositorio |
| [Modulo8_Deployment_Front](https://github.com/alzamoralabs/Modulo8_Deployment_Front) | Frontend — Streamlit |