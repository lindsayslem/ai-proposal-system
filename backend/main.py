from fastapi import FastAPI
from routes import proposals
from database import Base, engine
from routes.clients import router as clients_router

app = FastAPI(title="AI Proposal System")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "OK"}

app.include_router(proposals.router)
app.include_router(clients_router)