"""A cron job can prohibit hidden review writes without disabling its own work."""

from unittest.mock import MagicMock, patch

import pytest

from cron.scheduler import run_job


@pytest.mark.parametrize("policy", [None, True, False])
def test_job_review_policy_preserves_task_execution_and_report(tmp_path, policy):
    job = {"id": "audit-test", "name": "audit-test", "prompt": "inspect", "deliver": "local"}
    if policy is not None:
        job["background_review"] = policy

    task_marker = tmp_path / "explicit-task-output"
    review_settings = []

    class TaskAgent:
        def __init__(self, **kwargs):
            review_settings.append(kwargs.get("background_review_enabled", True))

        def run_conversation(self, prompt):
            # Explicit task work must still run, even when background review
            # is disabled. No model or external service is used in this test.
            task_marker.write_text("task completed")
            return {"final_response": "audit report", "completed": True}

        def close(self):
            pass

    with patch("cron.scheduler._hermes_home", tmp_path), \
         patch("cron.scheduler._resolve_origin", return_value=None), \
         patch("dotenv.load_dotenv"), \
         patch("hermes_state.SessionDB", return_value=MagicMock()), \
         patch("hermes_cli.runtime_provider.resolve_runtime_provider", return_value={
             "provider": "openrouter", "api_key": "test-only",
             "base_url": "https://example.invalid/v1", "api_mode": "chat_completions",
         }), \
         patch("run_agent.AIAgent", TaskAgent):
        success, document, report, error = run_job(job)

    assert success and error is None
    assert task_marker.read_text() == "task completed"
    assert report == "audit report" and report in document
    assert review_settings == [policy is not False]
