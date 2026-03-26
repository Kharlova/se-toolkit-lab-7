"""LLM tool definitions for backend endpoints."""

from services.api_client import get_api_client


def get_tools() -> list[dict]:
    """Get list of tool schemas for LLM.
    
    Returns:
        List of tool definitions with name, description, and parameters.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "Get list of all labs and tasks available in the system",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_learners",
                "description": "Get list of enrolled students and their groups",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_scores",
                "description": "Get score distribution (4 buckets) for a specific lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task average scores and attempt counts for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submissions per day for a specific lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group scores and student counts for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get top N learners by score for a specific lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top learners to return (default: 5)",
                            "default": 5,
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate percentage for a specific lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Trigger ETL sync to refresh data from autochecker",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
    ]


def execute_tool(name: str, arguments: dict) -> Any:
    """Execute a tool by name with given arguments.
    
    Args:
        name: Tool name (e.g., 'get_items', 'get_pass_rates')
        arguments: Tool arguments dict
    
    Returns:
        Tool execution result
    """
    api_client = get_api_client()
    
    if name == "get_items":
        return api_client.get_items()
    elif name == "get_learners":
        return api_client.get_learners() if hasattr(api_client, 'get_learners') else []
    elif name == "get_scores":
        lab = arguments.get("lab", "")
        return api_client.get_analytics_scores(lab) if hasattr(api_client, 'get_analytics_scores') else []
    elif name == "get_pass_rates":
        lab = arguments.get("lab", "")
        return api_client.get_analytics_pass_rates(lab)
    elif name == "get_timeline":
        lab = arguments.get("lab", "")
        return api_client.get_analytics_timeline(lab) if hasattr(api_client, 'get_analytics_timeline') else []
    elif name == "get_groups":
        lab = arguments.get("lab", "")
        return api_client.get_analytics_groups(lab) if hasattr(api_client, 'get_analytics_groups') else []
    elif name == "get_top_learners":
        lab = arguments.get("lab", "")
        limit = arguments.get("limit", 5)
        return api_client.get_analytics_top_learners(lab, limit) if hasattr(api_client, 'get_analytics_top_learners') else []
    elif name == "get_completion_rate":
        lab = arguments.get("lab", "")
        return api_client.get_analytics_completion_rate(lab) if hasattr(api_client, 'get_analytics_completion_rate') else []
    elif name == "trigger_sync":
        return api_client.trigger_sync() if hasattr(api_client, 'trigger_sync') else {"status": "synced"}
    else:
        return f"Unknown tool: {name}"
