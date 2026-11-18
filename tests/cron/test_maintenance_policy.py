from pathlib import Path

from run_agent import AIAgent


def _agent(maintenance_allowed: bool) -> AIAgent:
    agent = object.__new__(AIAgent)
    agent.maintenance_allowed = maintenance_allowed
    return agent


def test_maintenance_policy_allows_everything_when_enabled():
    agent = _agent(True)
    assert agent._maintenance_policy_block_message(
        "skill_manage", {"action": "patch"}
    ) is None


def test_maintenance_policy_blocks_skill_and_delegation_writes():
    agent = _agent(False)
    assert agent._maintenance_policy_block_message(
        "skill_manage", {"action": "patch"}
    )
    assert agent._maintenance_policy_block_message("delegate_task", {"goal": "edit"})
    assert agent._maintenance_policy_block_message(
        "memory", {"action": "replace"}
    )


def test_maintenance_policy_allows_only_temporary_file_writes(tmp_path):
    agent = _agent(False)
    assert agent._maintenance_policy_block_message(
        "write_file", {"path": str(tmp_path / "result.json")}
    ) is None
    assert agent._maintenance_policy_block_message(
        "patch", {"path": str(Path.home() / ".hermes" / "config.yaml")}
    )
    assert agent._maintenance_policy_block_message(
        "write_file", {"path": "relative-output.json"}
    )
