print(">>> Importing main application...")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Main application: do not initialize external clients at import-time.
print(">>> Starting FastAPI application...")
app = FastAPI(title="Thai Labour Law - Supabase-backed API")
origins = [
    "http://localhost:3000",  # React dev
    "https://thai-labour-law-chatbot-for-employee.netlify.app",  # Production front-end
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # อนุญาต origin
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, PUT, DELETE, ...
    allow_headers=["*"],            # Authorization, Content-Type, ...
)

print(">>> Defining root and utility endpoints...")
@app.get("/")
async def root():
    return {"message": "Welcome to the Thai Labour Law API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/warmup")
async def warmup():
    """
    Endpoint to preload heavy resources after deployment.
    This can be called manually or via a post-deployment script.
    """
    from database.supabase_client import get_supabase_client
    from llm.chatbot_llm import get_llm
    
    # Preload resources
    get_supabase_client()
    get_llm()
    
    return {"status": "warmed up", "message": "Heavy resources loaded successfully"}

@app.get("/enable-llm-router")
async def enable_llm_router():
    """
    Endpoint to ensure LLM router is loaded.
    This can be used to trigger lazy loading of the LLM-related routes.
    """
    from llm import chatbot_router as routers_llm
    app.include_router(routers_llm.router, prefix="/llm", tags=["llm"])
    return {"status": "LLM router enabled"}

print(">>> Including routers...")
from routers import routers_act, routers_help, routers_section, routers_library, routers_conversation, routers_user, routers_judgment

# Include routers
print(">>> Setting up API routers...")
app.include_router(routers_act.router, prefix="/api", tags=["api"])
app.include_router(routers_section.router, prefix="/api", tags=["api"])
app.include_router(routers_library.router, prefix="/api", tags=["api"])
app.include_router(routers_judgment.router, prefix="/api", tags=["api"])
app.include_router(routers_conversation.router, prefix="/api", tags=["api"])
app.include_router(routers_user.router, prefix="/api", tags=["api"])
app.include_router(routers_help.router, prefix="", tags=["help"])

print(">>> Preloading heavy resources...")
from database.supabase_client import get_supabase_client
from llm.chatbot_llm import get_llm
get_supabase_client()
get_llm()
print(">>> Heavy resources loaded successfully.")
from llm import chatbot_router as routers_llm
app.include_router(routers_llm.router, prefix="/llm", tags=["llm"])
print(">>> LLM router included.")