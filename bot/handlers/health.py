"""Handler for /health command.

This handler calls the LMS backend API to check system health.
"""

import httpx
from services.api_client import get_api_client


def handle_health() -> str:
    """Handle /health command.
    
    Returns:
        Backend health status with error details if failed.
    """
    try:
        client = get_api_client()
        result = client.health_check()
        return f"🟢 Backend is healthy. {result['item_count']} items available."
    except httpx.ConnectError as e:
        # Extract the actual error message
        error_msg = str(e)
        if "Connection refused" in error_msg:
            return f"🔴 Backend error: connection refused. Check that the services are running."
        elif "Connection timed out" in error_msg:
            return f"🔴 Backend error: connection timed out. The service may be overloaded."
        else:
            return f"🔴 Backend error: {error_msg}"
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code if e.response else "unknown"
        return f"🔴 Backend error: HTTP {status_code}. The backend service may be down."
    except httpx.RequestError as e:
        return f"🔴 Backend error: {str(e)}. Check your network and backend URL."
    except Exception as e:
        return f"🔴 Backend error: {str(e)}"
