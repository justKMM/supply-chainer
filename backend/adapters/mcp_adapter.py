"""MCP adapter — JSON-RPC 2.0 client/server for Model Context Protocol."""

from __future__ import annotations

import requests
from typing import Any

from backend.schemas import (
    AgentFact,
    AgentProtocolMessage,
    AgentProtocolReceipt,
    LiveMessage,
    McpToolCallParams,
    McpToolCallResult,
    McpToolDefinition,
    McpToolsListResult,
    make_id,
)
from backend.services.registry_service import registry


# ── Tool derivation ──────────────────────────────────────────────────────────

def agent_tools_from_fact(agent: AgentFact) -> list[McpToolDefinition]:
    """Derive MCP tool definitions from an agent's supported_message_types."""
    tools: list[McpToolDefinition] = []
    msg_types = agent.network.supported_message_types if agent.network else []
    for mt in msg_types:
        tools.append(McpToolDefinition(
            name=mt,
            description=f"Send a '{mt}' message to {agent.name}",
            inputSchema={
                "type": "object",
                "properties": {
                    "payload": {"type": "object", "description": "Message payload"},
                    "from_agent": {"type": "string", "description": "Sender agent ID"},
                },
                "required": ["payload"],
            },
        ))
    return tools


# ── JSON-RPC response builders ───────────────────────────────────────────────

def build_tools_list_response(agent: AgentFact, request_id: Any) -> dict:
    """Build a JSON-RPC 2.0 response for tools/list."""
    tools = agent_tools_from_fact(agent)
    result = McpToolsListResult(tools=tools)
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result.model_dump(),
    }


def build_tool_call_response(
    agent: AgentFact,
    request_id: Any,
    params: dict,
    from_agent: str = "",
) -> tuple[dict, AgentProtocolReceipt]:
    """Handle tools/call: execute the tool and return JSON-RPC response + receipt."""
    tool_params = McpToolCallParams(**params)

    # Verify tool exists
    available = {t.name for t in agent_tools_from_fact(agent)}
    if tool_params.name not in available:
        return build_error_response(request_id, -32602, f"Unknown tool: {tool_params.name}"), AgentProtocolReceipt(
            status="rejected", detail=f"Unknown tool: {tool_params.name}",
        )

    # Log the message via registry
    msg_id = make_id("mcp")
    lm = LiveMessage(
        message_id=msg_id,
        from_id=from_agent or "mcp-client",
        from_label=from_agent or "mcp-client",
        to_id=agent.agent_id,
        to_label=agent.name,
        type=tool_params.name,
        summary=str(tool_params.arguments)[:120] if tool_params.arguments else "",
        detail=f"MCP tools/call: {tool_params.name}",
    )
    registry.log_message(lm)

    # Build result
    tool_result = McpToolCallResult(
        content=[{"type": "text", "text": f"Tool '{tool_params.name}' executed on {agent.name}"}],
        isError=False,
    )
    receipt = AgentProtocolReceipt(
        message_id=msg_id,
        from_agent=from_agent,
        to_agent=agent.agent_id,
        status="accepted",
        detail=f"MCP tool call: {tool_params.name}",
    )

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": tool_result.model_dump(),
    }, receipt


def build_error_response(request_id: Any, code: int, message: str) -> dict:
    """Build a JSON-RPC 2.0 error response."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


# ── Client-side send ────────────────────────────────────────────────────────

def send_mcp(endpoint: str, message: AgentProtocolMessage, agent: AgentFact) -> AgentProtocolReceipt:
    """Send a message via MCP protocol.

    If endpoint is empty, performs local in-process delivery.
    Otherwise, POSTs a JSON-RPC tools/call to the remote endpoint.
    """
    if not endpoint:
        # Local in-process delivery: log and return accepted
        lm = LiveMessage(
            message_id=message.message_id,
            from_id=message.from_agent,
            from_label=message.from_agent,
            to_id=message.to_agent,
            to_label=agent.name if agent else message.to_agent,
            type=message.message_type or "mcp_message",
            summary=str(message.payload)[:120] if message.payload else "",
            detail="Delivered via MCP (local)",
        )
        registry.log_message(lm)
        return AgentProtocolReceipt(
            message_id=message.message_id,
            from_agent=message.from_agent,
            to_agent=message.to_agent,
            status="accepted",
            detail="Delivered via MCP (local)",
        )

    # Remote delivery: POST JSON-RPC tools/call
    try:
        jsonrpc_request = {
            "jsonrpc": "2.0",
            "id": make_id("rpc"),
            "method": "tools/call",
            "params": {
                "name": message.message_type or "message",
                "arguments": {
                    "payload": message.payload,
                    "from_agent": message.from_agent,
                },
            },
        }
        resp = requests.post(
            endpoint,
            json=jsonrpc_request,
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        if resp.ok:
            return AgentProtocolReceipt(
                message_id=message.message_id,
                from_agent=message.from_agent,
                to_agent=message.to_agent,
                status="accepted",
                detail="Delivered via MCP (remote)",
            )
        return AgentProtocolReceipt(
            message_id=message.message_id,
            from_agent=message.from_agent,
            to_agent=message.to_agent,
            status="rejected",
            detail=f"MCP remote HTTP {resp.status_code}",
        )
    except Exception as exc:
        return AgentProtocolReceipt(
            message_id=message.message_id,
            from_agent=message.from_agent,
            to_agent=message.to_agent,
            status="error",
            detail=f"MCP send error: {exc}",
        )
