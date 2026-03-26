"""LLM client with tool calling support."""

import json
import logging
import sys
from typing import Any, Optional
import httpx
from config import load_config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClient:
    """Client for LLM API with tool calling support."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """Initialize LLM client.
        
        Args:
            base_url: LLM API base URL (default from config)
            api_key: LLM API key (default from config)
            model: Model name (default from config)
        """
        config = load_config()
        self.base_url = base_url or config["llm_api_base_url"]
        self.api_key = api_key or config["llm_api_key"]
        self.model = model or config["llm_api_model"]
        self._client: Optional[httpx.Client] = None

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client with auth headers."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=60.0
            )
        return self._client

    def chat(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        system_prompt: Optional[str] = None,
    ) -> dict:
        """Send chat request to LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: List of tool schemas (optional)
            system_prompt: System prompt to prepend (optional)
        
        Returns:
            LLM response dict with 'content' and optional 'tool_calls'
        """
        client = self._get_client()
        
        # Build messages with system prompt
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)
        
        # Build request body
        body = {
            "model": self.model,
            "messages": all_messages,
        }
        
        if tools:
            body["tools"] = tools
            body["tool_choice"] = "auto"
        
        response = client.post("/chat/completions", json=body)
        response.raise_for_status()
        data = response.json()
        
        choice = data["choices"][0]["message"]
        result = {"content": choice.get("content", "")}
        
        # Extract tool calls if present
        if "tool_calls" in choice and choice["tool_calls"]:
            result["tool_calls"] = []
            for tc in choice["tool_calls"]:
                result["tool_calls"].append({
                    "id": tc["id"],
                    "name": tc["function"]["name"],
                    "arguments": json.loads(tc["function"]["arguments"]),
                })
        
        return result

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None


# Global client instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create global LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
