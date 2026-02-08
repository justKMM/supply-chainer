"""A2A adapter — Google Agent-to-Agent protocol with agent cards and task lifecycle."""

from __future__ import annotations

import requests
from datetime import datetime
from typing import Any

from backend.schemas import (
    A2AAgentCapabilities,
    A2AAgentCard,
    A2AAgentSkill,
    A2AArtifact,
    A2AMessage,
    A2APart,
    A2ATask,
    A2ATaskSendParams,
    A2ATaskStatus,
    AgentFact,
    AgentProtocolMessage,
    AgentProtocolReceipt,
    LiveMessage,
    make_id,
)
from backend.services.registry_service import registry


# ── In-memory task store ─────────────────────────────────────────────────────

_task_store: dict[str, A2ATask] = {}


def get_task_store() -> dict[str, A2ATask]:
    return _task_store


def clear_task_store() -> None:
    _task_store.clear()


# ── Agent card generation ────────────────────────────────────────────────────

def generate_agent_card(agent: AgentFact) -> A2AAgentCard:
    """Build an A2A agent card from an AgentFact."""
    msg_types = agent.network.supported_message_types if agent.network else []
    skills = [
        A2AAgentSkill(
            id=mt,
            name=mt.replace("_", " ").title(),
            description=f"Handle '{mt}' messages for {agent.name}",
            tags=[agent.role, mt],
            examples=[f"Send a {mt} to {agent.name}"],
        )
        for mt in msg_types
    ]
    endpoint = agent.network.endpoint if agent.network else ""
    return A2AAgentCard(
        name=agent.name,
        description=agent.description or f"{agent.name} ({agent.role})",
        url=endpoint,
        version=agent.network.api_version if agent.network else "1.0",
        capabilities=A2AAgentCapabilities(
            streaming=False,
            pushNotifications=False,
            stateTransitionHistory=True,
        ),
        skills=skills,
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/plain"],
    )


# ── Task lifecycle ───────────────────────────────────────────────────────────

def create_task_from_message(agent: AgentFact, message: dict) -> A2ATask:
    """Create an A2A task from an incoming message payload."""
    task_id = message.get("id", make_id("task"))
    session_id = message.get("sessionId", make_id("session"))

    # Extract user message
    msg_data = message.get("message", {})
    parts = [A2APart(**p) for p in msg_data.get("parts", [{"type": "text", "text": ""}])]
    user_msg = A2AMessage(role=msg_data.get("role", "user"), parts=parts)

    task = A2ATask(
        id=task_id,
        sessionId=session_id,
        status=A2ATaskStatus(state="submitted"),
        history=[user_msg],
    )
    _task_store[task_id] = task
    return task


def process_task(agent: AgentFact, task: A2ATask, message: A2AMessage) -> A2ATask:
    """Process a task: submitted -> working -> completed."""
    # Transition to working
    task.status = A2ATaskStatus(state="working")

    # Generate response
    input_text = message.parts[0].text if message.parts else ""
    response_text = f"[{agent.name}] Processed: {input_text[:100]}" if input_text else f"[{agent.name}] Task completed"

    # Create agent response message
    agent_msg = A2AMessage(
        role="agent",
        parts=[A2APart(type="text", text=response_text)],
    )
    task.history.append(agent_msg)

    # Add artifact
    task.artifacts = [A2AArtifact(
        name="result",
        description=f"Result from {agent.name}",
        parts=[A2APart(type="text", text=response_text)],
    )]

    # Transition to completed
    task.status = A2ATaskStatus(
        state="completed",
        message=agent_msg,
    )

    _task_store[task.id] = task
    return task


# ── Client-side send ────────────────────────────────────────────────────────

def send_a2a(endpoint: str, message: AgentProtocolMessage, agent: AgentFact) -> AgentProtocolReceipt:
    """Send a message via A2A protocol.

    If endpoint is empty, performs local in-process delivery (create + process task).
    Otherwise, POSTs a JSON-RPC tasks/send to the remote endpoint.
    """
    if not endpoint:
        # Local in-process delivery
        user_msg = A2AMessage(
            role="user",
            parts=[A2APart(type="text", text=str(message.payload) if message.payload else "")],
        )
        task = A2ATask(
            status=A2ATaskStatus(state="submitted"),
            history=[user_msg],
        )
        _task_store[task.id] = task
        task = process_task(agent, task, user_msg)

        # Log the message
        lm = LiveMessage(
            message_id=message.message_id,
            from_id=message.from_agent,
            from_label=message.from_agent,
            to_id=message.to_agent,
            to_label=agent.name if agent else message.to_agent,
            type=message.message_type or "a2a_message",
            summary=str(message.payload)[:120] if message.payload else "",
            detail=f"A2A task {task.id} completed (local)",
        )
        registry.log_message(lm)

        return AgentProtocolReceipt(
            message_id=message.message_id,
            from_agent=message.from_agent,
            to_agent=message.to_agent,
            status="accepted",
            detail=f"A2A task {task.id} completed (local)",
        )

    # Remote delivery: POST JSON-RPC tasks/send
    try:
        jsonrpc_request = {
            "jsonrpc": "2.0",
            "id": make_id("rpc"),
            "method": "tasks/send",
            "params": {
                "id": make_id("task"),
                "sessionId": make_id("session"),
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": str(message.payload) if message.payload else ""}],
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
                detail="A2A delivered (remote)",
            )
        return AgentProtocolReceipt(
            message_id=message.message_id,
            from_agent=message.from_agent,
            to_agent=message.to_agent,
            status="rejected",
            detail=f"A2A remote HTTP {resp.status_code}",
        )
    except Exception as exc:
        return AgentProtocolReceipt(
            message_id=message.message_id,
            from_agent=message.from_agent,
            to_agent=message.to_agent,
            status="error",
            detail=f"A2A send error: {exc}",
        )
