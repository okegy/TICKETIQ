from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.routers import analysis, knowledge

app = FastAPI(
    title="TicketIQ AI Service",
    description="AI Service for IT Support Resolution Copilot",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router, prefix="/ai", tags=["analysis"])
app.include_router(knowledge.router, prefix="/ai", tags=["knowledge"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "TicketIQ AI"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
