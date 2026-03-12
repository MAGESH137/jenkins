"""
Task Analytics Service
Jenkins Practice - Python Flask Microservice

Provides analytics/reporting over the Task Manager API.
"""

import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_BASE = os.getenv("TASK_API_URL", "http://localhost:8080/api")


# ── In-memory analytics store ─────────────────────────────────────────────────

_event_log: list[dict] = []


def log_event(event_type: str, payload: dict) -> dict:
    """Record an analytics event."""
    event = {
        "id":         len(_event_log) + 1,
        "type":       event_type,
        "payload":    payload,
        "timestamp":  datetime.utcnow().isoformat() + "Z",
    }
    _event_log.append(event)
    return event


# ── Analytics helpers ─────────────────────────────────────────────────────────

def calculate_completion_rate(tasks: list) -> float:
    """Return the percentage of completed tasks (0–100)."""
    if not tasks:
        return 0.0
    completed = sum(1 for t in tasks if t.get("completed"))
    return round(completed / len(tasks) * 100, 2)


def group_by_priority(tasks: list) -> dict:
    """Count tasks per priority level."""
    counts: dict[str, int] = {}
    for task in tasks:
        priority = task.get("priority", "UNKNOWN")
        counts[priority] = counts.get(priority, 0) + 1
    return counts


def get_overdue_tasks(tasks: list) -> list:
    """
    Return tasks that are not completed and are considered overdue.
    In a real system this would compare due dates; here we flag
    all HIGH-priority incomplete tasks as 'overdue' for demo purposes.
    """
    return [t for t in tasks if not t.get("completed") and t.get("priority") == "HIGH"]


def build_summary(tasks: list) -> dict:
    """Build a full analytics summary dict from a task list."""
    total     = len(tasks)
    completed = sum(1 for t in tasks if t.get("completed"))
    pending   = total - completed

    return {
        "total":            total,
        "completed":        completed,
        "pending":          pending,
        "completion_rate":  calculate_completion_rate(tasks),
        "by_priority":      group_by_priority(tasks),
        "overdue_count":    len(get_overdue_tasks(tasks)),
        "generated_at":     datetime.utcnow().isoformat() + "Z",
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return jsonify({"status": "UP", "service": "task-analytics", "version": "1.0.0"})


@app.get("/analytics/summary")
def summary():
    """
    Return a summary computed from tasks supplied in the request body,
    or from a small built-in sample when no body is provided.
    This avoids a live dependency on the Java API for tests/demo.
    """
    data = request.get_json(silent=True)

    if data and "tasks" in data:
        tasks = data["tasks"]
    else:
        # Built-in demo dataset
        tasks = [
            {"id": 1, "title": "Task A", "priority": "HIGH",   "completed": False},
            {"id": 2, "title": "Task B", "priority": "MEDIUM", "completed": True},
            {"id": 3, "title": "Task C", "priority": "LOW",    "completed": True},
            {"id": 4, "title": "Task D", "priority": "HIGH",   "completed": False},
            {"id": 5, "title": "Task E", "priority": "MEDIUM", "completed": False},
        ]

    result = build_summary(tasks)
    log_event("SUMMARY_REQUESTED", {"task_count": len(tasks)})
    return jsonify(result)


@app.get("/analytics/completion-rate")
def completion_rate():
    data  = request.get_json(silent=True) or {}
    tasks = data.get("tasks", [])
    rate  = calculate_completion_rate(tasks)
    return jsonify({"completion_rate": rate, "task_count": len(tasks)})


@app.get("/analytics/priority-breakdown")
def priority_breakdown():
    data  = request.get_json(silent=True) or {}
    tasks = data.get("tasks", [])
    breakdown = group_by_priority(tasks)
    return jsonify({"by_priority": breakdown, "total": len(tasks)})


@app.post("/analytics/events")
def record_event():
    data = request.get_json(silent=True) or {}
    if "type" not in data:
        return jsonify({"error": "Missing required field: type"}), 400
    event = log_event(data["type"], data.get("payload", {}))
    return jsonify(event), 201


@app.get("/analytics/events")
def list_events():
    limit  = min(int(request.args.get("limit", 50)), 200)
    events = _event_log[-limit:]
    return jsonify({"events": events, "count": len(events)})


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
