from __future__ import annotations

from backend.services.registry_service import registry
from backend.services.agent_transport import send_to_agent
from backend.schemas import AgentProtocolMessage

from backend.agents.core import core_agents
from backend.agents.suppliers import supplier_agents


def test_send_to_agent_mcp_logs_and_returns_accepted():
	# start with a clean registry
	registry.clear()

	# Use real agents from the agents folder
	core = core_agents()
	suppliers = supplier_agents()

	# sender: Ferrari Procurement (from core_agents)
	sender = next((a for a in core if a.agent_id == "ferrari-procurement-01"), None)
	assert sender is not None

	# recipient: pick a supplier (Brembo) and switch it to MCP transport for the test
	recipient = next((a for a in suppliers if a.agent_id == "brembo-brake-supplier-01"), None)
	assert recipient is not None
	recipient.network.protocol = "MCP"
	recipient.network.endpoint = ""

	# register both agents in the in-memory registry
	registry.register(sender)
	registry.register(recipient)

	# Build protocol message and send
	msg = AgentProtocolMessage(
		from_agent=sender.agent_id,
		to_agent=recipient.agent_id,
		message_type="test.mcp",
		payload={"hello": "mcp"},
	)

	receipt = send_to_agent(msg)

	assert receipt is not None
	assert receipt.message_id == msg.message_id
	assert receipt.status == "accepted"

	# Ensure registry recorded the live message
	messages = registry.get_messages()
	assert any(m.message_id == msg.message_id for m in messages)

	# Cleanup
	registry.clear()
