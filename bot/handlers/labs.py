"""Handler for /labs command."""

import httpx
from services.api_client import get_api_client


def handle_labs() -> str:
    """Handle /labs command.
    
    Returns:
        Formatted list of available labs from the backend.
    """
    try:
        client = get_api_client()
        items = client.get_items()
        
        # Filter only labs (not tasks)
        labs = [item for item in items if item.get("type") == "lab"]
        
        if not labs:
            return "📚 No labs available."
        
        lab_list = "\n".join([f"- {lab['title']}" for lab in labs])
        return f"📚 Available labs:\n{lab_list}"
        
    except httpx.ConnectError as e:
        return f"🔴 Backend error: connection refused. Check that the services are running."
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code if e.response else "unknown"
        return f"🔴 Backend error: HTTP {status_code}. The backend service may be down."
    except httpx.RequestError as e:
        return f"🔴 Backend error: {str(e)}"
    except Exception as e:
        return f"🔴 Backend error: {str(e)}"
