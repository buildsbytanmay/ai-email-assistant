from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import web, api
from app.database.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Email Assistant", description="An open-source AI-powered email understanding and response generation tool.")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(web.router)
app.include_router(api.router)
