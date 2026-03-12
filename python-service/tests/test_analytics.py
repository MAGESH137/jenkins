"""
Pytest test suite for Task Analytics Service.
Run with: pytest tests/ -v --cov=app --cov-report=term-missing
"""

import pytest
import json
from app import app, calculate_completion_rate, group_by_priority, get_overdue_tasks, build_summary, _event_log


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """Flask test client with testing mode enabled."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_tasks():
    return [
        {"id": 1, "title": "Design API",       "priority": "HIGH",   "completed": True},
        {"id": 2, "title": "Write tests",       "priority": "HIGH",   "completed": False},
        {"id": 3, "title": "Set up Jenkins",    "priority": "MEDIUM", "completed": True},
        {"id": 4, "title": "Deploy to staging", "priority": "MEDIUM", "completed": False},
        {"id": 5, "title": "Update README",     "priority": "LOW",    "completed": True},
    ]


@pytest.fixture
def all_completed():
    return [{"id": i, "title": f"Task {i}", "priority": "LOW", "completed": True} for i in range(1, 6)]


@pytest.fixture
def none_completed():
    return [{"id": i, "title": f"Task {i}", "priority": "MEDIUM", "completed": False} for i in range(1, 4)]


# ── Unit tests: calculate_completion_rate ─────────────────────────────────────

class TestCompletionRate:
    def test_empty_list_returns_zero(self):
        assert calculate_completion_rate([]) == 0.0

    def test_all_completed_returns_100(self, all_completed):
        assert calculate_completion_rate(all_completed) == 100.0

    def test_none_completed_returns_zero(self, none_completed):
        assert calculate_completion_rate(none_completed) == 0.0

    def test_partial_completion(self, sample_tasks):
        rate = calculate_completion_rate(sample_tasks)
        assert rate == 60.0  # 3 out of 5

    def test_single_completed(self):
        assert calculate_completion_rate([{"completed": True}]) == 100.0

    def test_single_not_completed(self):
        assert calculate_completion_rate([{"completed": False}]) == 0.0

    def test_returns_float(self, sample_tasks):
        assert isinstance(calculate_completion_rate(sample_tasks), float)

    def test_result_is_rounded_to_two_decimals(self):
        tasks = [{"completed": True}] + [{"completed": False}] * 2
        rate = calculate_completion_rate(tasks)
        assert rate == round(rate, 2)


# ── Unit tests: group_by_priority ─────────────────────────────────────────────

class TestGroupByPriority:
    def test_empty_list(self):
        assert group_by_priority([]) == {}

    def test_single_priority(self):
        tasks = [{"priority": "HIGH"}, {"priority": "HIGH"}]
        result = group_by_priority(tasks)
        assert result == {"HIGH": 2}

    def test_multiple_priorities(self, sample_tasks):
        result = group_by_priority(sample_tasks)
        assert result["HIGH"]   == 2
        assert result["MEDIUM"] == 2
        assert result["LOW"]    == 1

    def test_unknown_priority_handled(self):
        tasks = [{"title": "No priority set"}]  # missing priority key
        result = group_by_priority(tasks)
        assert "UNKNOWN" in result

    def test_all_same_priority(self, all_completed):
        result = group_by_priority(all_completed)
        assert result == {"LOW": 5}


# ── Unit tests: get_overdue_tasks ─────────────────────────────────────────────

class TestGetOverdueTasks:
    def test_empty_list(self):
        assert get_overdue_tasks([]) == []

    def test_no_overdue(self, all_completed):
        assert get_overdue_tasks(all_completed) == []

    def test_high_incomplete_are_overdue(self, sample_tasks):
        overdue = get_overdue_tasks(sample_tasks)
        assert len(overdue) == 1
        assert overdue[0]["title"] == "Write tests"

    def test_completed_high_not_overdue(self):
        tasks = [{"priority": "HIGH", "completed": True, "title": "Done high"}]
        assert get_overdue_tasks(tasks) == []

    def test_medium_incomplete_not_overdue(self):
        tasks = [{"priority": "MEDIUM", "completed": False, "title": "Medium task"}]
        assert get_overdue_tasks(tasks) == []


# ── Unit tests: build_summary ─────────────────────────────────────────────────

class TestBuildSummary:
    def test_summary_keys_present(self, sample_tasks):
        summary = build_summary(sample_tasks)
        required = ["total", "completed", "pending", "completion_rate", "by_priority", "overdue_count", "generated_at"]
        for key in required:
            assert key in summary, f"Missing key: {key}"

    def test_correct_totals(self, sample_tasks):
        s = build_summary(sample_tasks)
        assert s["total"]     == 5
        assert s["completed"] == 3
        assert s["pending"]   == 2

    def test_completion_rate_matches(self, sample_tasks):
        s = build_summary(sample_tasks)
        assert s["completion_rate"] == 60.0

    def test_empty_tasks(self):
        s = build_summary([])
        assert s["total"]           == 0
        assert s["completion_rate"] == 0.0

    def test_generated_at_is_iso_string(self, sample_tasks):
        s = build_summary(sample_tasks)
        assert "T" in s["generated_at"]
        assert s["generated_at"].endswith("Z")


# ── Integration tests: HTTP endpoints ─────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_status_up(self, client):
        data = resp_json(client.get("/health"))
        assert data["status"] == "UP"

    def test_health_service_name(self, client):
        data = resp_json(client.get("/health"))
        assert data["service"] == "task-analytics"


class TestSummaryEndpoint:
    def test_default_demo_data(self, client):
        resp = client.get("/analytics/summary")
        assert resp.status_code == 200
        data = resp_json(resp)
        assert data["total"] > 0

    def test_with_custom_tasks(self, client, sample_tasks):
        resp = client.get(
            "/analytics/summary",
            data=json.dumps({"tasks": sample_tasks}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp_json(resp)
        assert data["total"]     == 5
        assert data["completed"] == 3

    def test_empty_tasks(self, client):
        resp = client.get(
            "/analytics/summary",
            data=json.dumps({"tasks": []}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp_json(resp)
        assert data["completion_rate"] == 0.0


class TestCompletionRateEndpoint:
    def test_returns_rate(self, client, sample_tasks):
        resp = client.get(
            "/analytics/completion-rate",
            data=json.dumps({"tasks": sample_tasks}),
            content_type="application/json",
        )
        data = resp_json(resp)
        assert data["completion_rate"] == 60.0
        assert data["task_count"]      == 5

    def test_empty_body(self, client):
        resp = client.get("/analytics/completion-rate")
        assert resp.status_code == 200
        data = resp_json(resp)
        assert data["completion_rate"] == 0.0


class TestPriorityBreakdownEndpoint:
    def test_returns_breakdown(self, client, sample_tasks):
        resp = client.get(
            "/analytics/priority-breakdown",
            data=json.dumps({"tasks": sample_tasks}),
            content_type="application/json",
        )
        data = resp_json(resp)
        assert data["by_priority"]["HIGH"]   == 2
        assert data["by_priority"]["MEDIUM"] == 2
        assert data["by_priority"]["LOW"]    == 1


class TestEventsEndpoint:
    def test_post_event(self, client):
        resp = client.post(
            "/analytics/events",
            data=json.dumps({"type": "TASK_CREATED", "payload": {"task_id": 1}}),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp_json(resp)
        assert data["type"] == "TASK_CREATED"
        assert "timestamp" in data
        assert "id" in data

    def test_post_event_missing_type(self, client):
        resp = client.post(
            "/analytics/events",
            data=json.dumps({"payload": {}}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_list_events(self, client):
        # Record a few events first
        for i in range(3):
            client.post(
                "/analytics/events",
                data=json.dumps({"type": f"EVENT_{i}"}),
                content_type="application/json",
            )
        resp = client.get("/analytics/events")
        assert resp.status_code == 200
        data = resp_json(resp)
        assert data["count"] >= 3


# ── Helpers ───────────────────────────────────────────────────────────────────

def resp_json(resp):
    return json.loads(resp.data)
