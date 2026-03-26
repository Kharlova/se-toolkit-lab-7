"""Handler for /scores command."""

import httpx
from services.api_client import get_api_client


def handle_scores(lab: str) -> str:
    """Handle /scores command.
    
    Args:
        lab: Lab identifier (e.g., "lab-04")
    
    Returns:
        Formatted pass rates for the lab.
    """
    if not lab:
        return "⚠️ Please specify a lab. Usage: /scores lab-04"
    
    try:
        client = get_api_client()
        pass_rates = client.get_analytics_pass_rates(lab)
        
        if not pass_rates:
            return f"📊 No data found for {lab}. Check the lab identifier."
        
        lines = [f"📊 Pass rates for {lab}:"]
        for rate in pass_rates:
            task = rate.get("task", "Unknown")
            avg_score = rate.get("avg_score", 0)
            attempts = rate.get("attempts", 0)
            lines.append(f"- {task}: {avg_score:.1f}% ({attempts} attempts)")
        
        return "\n".join(lines)
        
    except httpx.ConnectError as e:
        return f"🔴 Backend error: connection refused. Check that the services are running."
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code if e.response else "unknown"
        return f"🔴 Backend error: HTTP {status_code}. The backend service may be down."
    except httpx.RequestError as e:
        return f"🔴 Backend error: {str(e)}"
    except Exception as e:
        return f"🔴 Backend error: {str(e)}"
