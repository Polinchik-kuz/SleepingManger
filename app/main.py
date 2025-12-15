from fastapi import FastAPI
from app.database import Base, engine
from app.config import settings
from app.routes import user, sleep, goal, analytics, reminder

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION
)

app.include_router(user.router, prefix="/api/users", tags=["Users"])
app.include_router(sleep.router, prefix="/api", tags=["Sleep Records"])
app.include_router(goal.router, prefix="/api", tags=["Goals"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(reminder.router, prefix="/api", tags=["Reminders"])

@app.get("/")
def root():
    return {
        "message": f"Добро пожаловать в {settings.PROJECT_NAME}!",
        "docs": "/docs",
        "version": settings.PROJECT_VERSION
    }
