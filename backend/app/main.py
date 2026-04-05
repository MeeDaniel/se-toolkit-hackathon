from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base
from app.routes import excursions, chat, statistics, users
from app.services import ai_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables and handle schema migrations
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Add user_id column if it doesn't exist (migration)
        try:
            await conn.execute("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'excursions' AND column_name = 'user_id'
                    ) THEN
                        ALTER TABLE excursions ADD COLUMN user_id INTEGER REFERENCES users(id);
                        -- Set default user_id for existing records
                        UPDATE excursions SET user_id = 1 WHERE user_id IS NULL;
                    END IF;
                    
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'users'
                    ) THEN
                        CREATE TABLE users (
                            id SERIAL PRIMARY KEY,
                            telegram_alias VARCHAR(100) UNIQUE NOT NULL,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            excursions INTEGER DEFAULT 0
                        );
                    END IF;
                END $$;
            """)
        except Exception as e:
            print(f"Migration note: {e}")
    yield
    # Shutdown: Clean up resources if needed
    await engine.dispose()


app = FastAPI(
    title="TourStats API",
    description="AI-powered statistics app for Innopolis tour guides",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",  # Custom docs path
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(excursions.router, prefix="/api/excursions", tags=["excursions"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["statistics"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {
        "message": "TourStats API",
        "docs": "/api/docs",
        "health": "/api/health",
    }
