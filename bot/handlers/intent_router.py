"""Intent router using LLM for natural language queries.

The router uses tool calling to let the LLM decide which API endpoints to call.
"""

import json
import logging
import sys
from typing import Any

from services.llm_client import get_llm_client
from services.llm_tools import get_tools, execute_tool
from services.api_client import get_api_client


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS). 
You have access to tools that fetch data about labs, students, scores, and analytics.

When the user asks a question:
1. Think about what data they need
2. Call the appropriate tool(s) to get that data
3. Use the tool results to provide a clear, helpful answer

Available tools:
- get_items: List all labs and tasks
- get_learners: List enrolled students
- get_scores: Score distribution for a lab
- get_pass_rates: Per-task pass rates for a lab
- get_timeline: Submissions per day for a lab
- get_groups: Per-group performance for a lab
- get_top_learners: Top N students for a lab
- get_completion_rate: Completion percentage for a lab
- trigger_sync: Refresh data from autochecker

If the user asks about "labs", "courses", or "what's available" — use get_items.
If the user asks about "scores", "pass rates", "results" for a specific lab — use get_pass_rates or get_scores.
If the user asks about "top students", "best performers" — use get_top_learners.
If the user asks about "groups" or "which group is best" — use get_groups.
If the user asks about "completion" or "how many finished" — use get_completion_rate.
If the user asks to compare labs — you may need to call get_pass_rates for multiple labs.

For greetings or unclear messages, respond helpfully without using tools.
If you don't understand, ask for clarification or suggest what you can help with.

Lab identifiers are like: lab-01, lab-02, lab-03, lab-04, lab-05, lab-06, lab-07.
When a user says "lab 4" or "lab four", convert to "lab-04"."""


def route_intent(message: str, debug: bool = True) -> str:
    """Route user message through LLM to get response.
    
    Args:
        message: User's message text
        debug: Whether to print debug info to stderr
    
    Returns:
        Response text
    """
    llm_client = get_llm_client()
    tools = get_tools()
    
    # Conversation history
    messages = [{"role": "user", "content": message}]
    
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Call LLM
        try:
            result = llm_client.chat(messages=messages, tools=tools, system_prompt=SYSTEM_PROMPT)
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return f"LLM error: {str(e)}. Try again later."
        
        content = result.get("content", "")
        tool_calls = result.get("tool_calls", [])
        
        # If no tool calls, return the content
        if not tool_calls:
            if content:
                return content
            return "I didn't understand. Can you rephrase? I can help with labs, scores, pass rates, top students, and more."
        
        # Execute tools and collect results
        tool_results = []
        for tc in tool_calls:
            tool_name = tc["name"]
            tool_args = tc["arguments"]
            
            if debug:
                print(f"[tool] LLM called: {tool_name}({json.dumps(tool_args)})", file=sys.stderr)
            
            try:
                tool_result = execute_tool(tool_name, tool_args)
                if debug:
                    result_summary = str(tool_result)[:200]
                    if isinstance(tool_result, list):
                        result_summary = f"{len(tool_result)} items"
                    print(f"[tool] Result: {result_summary}", file=sys.stderr)
            except Exception as e:
                tool_result = f"Error: {str(e)}"
                if debug:
                    print(f"[tool] Error: {tool_result}", file=sys.stderr)
            
            tool_results.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": json.dumps(tool_result) if not isinstance(tool_result, str) else tool_result,
            })
        
        # Feed tool results back to LLM
        if debug:
            print(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM", file=sys.stderr)
        
        messages.extend(tool_results)
    
    # If we reach here, return whatever content we have
    if content:
        return content
    return "I processed your request but couldn't generate a complete answer."
