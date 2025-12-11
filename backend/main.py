from fastapi import FastAPI
from routes import proposals
from database import Base, engine
from routes.clients import router as clients_router
from routes.projects import router as projects_router
from routes.price_catalog import router as catalog_router
from routes.line_items import router as line_items_router
from routes.attachments import router as attachments_router
from routes.activity_logs import router as activity_router

app = FastAPI(title="AI Proposal System")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "OK"}

app.include_router(proposals.router)
app.include_router(clients_router)
app.include_router(projects_router)
app.include_router(catalog_router)
app.include_router(line_items_router)
app.include_router(attachments_router)
app.include_router(activity_router)
