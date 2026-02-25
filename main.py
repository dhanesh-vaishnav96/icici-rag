from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from chat import ask_question, RATE_LIMIT_RESPONSE

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="RAG Document Assistant API")
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    # Return 200 so the frontend naturally displays the message as a bot response
    return JSONResponse(
        status_code=200,
        content={"answer": RATE_LIMIT_RESPONSE},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    question: str


@app.get("/")
def root():
    return {"status": "✅ RAG Backend is running!", "endpoint": "POST /chat"}


@app.post("/chat")
@limiter.limit("50/minute")
def chat(request: Request, query: Query):
    try:
        answer = ask_question(query.question)
        return {"answer": answer}
    except Exception as e:

        return JSONResponse(
            status_code=200,
            content={"answer": f"⚠️ An unexpected error occurred: {str(e)}. Please try again."},
        )
