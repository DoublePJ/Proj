from fastapi import APIRouter

router = APIRouter(prefix="/help", tags=["help"])

@router.get("/")
def help_info():
    return {
        "message": "Thai Labour Law API - help",
        "endpoints": {
            "/": "Root welcome message",
            "/health": "Health check",
            "/warmup": "Preload heavy resources",
            "/enable-llm-router": "Enable LLM router (lazy load)",
            "/api": "Namespaced API endpoints under /api",
            "/llm": "LLM/chat endpoints (mounted at /llm)",
        },
    }

@router.get("/api")
def help_api():
    return {
        "endpoints": {
            "/api/acts": "Acts and related endpoints",
            "/api/sections": "Act sections endpoints",
            "/api/libraries": "Library resources (acts, books, groups, sections)",
            "/api/judgments": "Judgments endpoints",
            "/api/conversations": "Conversation and chat-room endpoints",
            "/api/users": "User profile and options endpoints",
        }
    }

@router.get("/api/sections")
def help_sections():
    return {
        "endpoints": {
            "/api/sections/by/section_id/{section_id}": "Get section by its ID",
            "/api/sections/by/act_id/{act_id}": "Get sections by act ID",
            "/api/sections/by/book_id/{book_id}": "Get sections by book ID",
            "/api/sections/by/group_id/{group_id}": "Get sections by group ID",
            "/api/sections/by/super_section_id/{super_section_id}": "Get sections by super section ID",
            "/api/sections/by/act_id/{act_id}/section_number/{section_number}": "Get section by act ID and section number",
            "/api/sections/by/act_id/{act_id}/search/{keyword}": "Search sections within an act",
            "/api/sections/search/{keyword}": "Search sections across acts",
        }
    }
    
@router.get("/api/acts")
def help_acts():
    return {
        "endpoints": {
            "/api/acts/by/act_id/{act_id}": "Get act by its ID",
            "/api/acts/": "Get all acts",
            "/api/acts/by/act_name/{act_name}": "Get act by its name",
            "/api/acts/search/{keyword}": "Search acts by keyword",
            "/api/acts/books/by/act_id/{act_id}": "Get books for an act",
            "/api/acts/books/by/book_id/{book_id}": "Get book by book ID",
            "/api/acts/books/by/act_id/{act_id}/book_number/{book_number}": "Get book by act ID and book number",
            "/api/acts/books/search/{keyword}": "Search books",
            "/api/acts/groups/by/book_id/{book_id}": "Get groups by book ID",
            "/api/acts/groups/by/group_id/{group_id}": "Get group by ID",
            "/api/acts/groups/by/act_id/{act_id}/group_number/{group_number}": "Get group by act ID and group number",
            "/api/acts/groups/search/{keyword}": "Search groups",
            "/api/acts/super_sections/by/act_id/{act_id}": "Get super sections by act ID",
            "/api/acts/super_sections/by/group_id/{group_id}": "Get super sections by group ID",
            "/api/acts/super_sections/by/super_section_id/{super_section_id}": "Get super section by ID",
            "/api/acts/super_sections/by/act_id/{act_id}/super_section_number/{super_section_number}": "Get super section by act ID and number",
        }
    }


@router.get("/api/libraries")
def help_libraries():
    return {
        "endpoints": {
            "/api/libraries/acts": "Get all acts in the library",
            "/api/libraries/act/{act_id}": "Get act details by ID",
            "/api/libraries/tags": "Get all tags",
            "/api/libraries/acts/{act_id}/books": "Get books for an act",
            "/api/libraries/books/{book_id}/groups": "Get groups for a book",
            "/api/libraries/groups/{group_id}/super_sections": "Get super sections for a group",
            "/api/libraries/super_sections/{super_section_id}/sections": "Get sections for a super section",
            "/api/libraries/sections/{act_id}/{section_number}": "Get section by act ID and section number",
            "/api/libraries/super_sections/{super_section_id}/sections_stream": "Stream sections (ndjson)",
        }
    }


@router.get("/api/conversations")
def help_conversations():
    return {
        "endpoints": {
            "/api/conversations/rooms [POST]": "Create a chat room",
            "/api/conversations/rooms [GET]": "List chat rooms",
            "/api/conversations/rooms/{room_id} [GET|PUT|DELETE]": "Manage a specific room",
            "/api/conversations/rooms/{room_id}/messages [POST|GET]": "Add or list messages",
            "/api/conversations/rooms/{room_id}/history [GET]": "Get conversation history formatted for LLM",
            "/api/conversations/rooms/by-user/{user_id} [DELETE]": "Delete all rooms for a user",
        }
    }


@router.get("/api/users")
def help_users():
    return {
        "endpoints": {
            "/api/users/ [POST]": "Create or update a user profile",
            "/api/users/{user_id} [GET|PUT|DELETE]": "Get/update/delete a user profile",
            "/api/users/options/jobs [GET]": "Get available job options",
            "/api/users/options/job-types [GET]": "Get job-type options",
        }
    }


@router.get("/llm")
def help_llm():
    return {
        "endpoints": {
            "/llm/chat [POST]": "Chat endpoint (synchronous)",
            "/llm/chat_stream [POST]": "Chat streaming endpoint (ndjson)"
        }
    }