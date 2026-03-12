import React, { useState, useEffect, useCallback } from 'react';
import TaskList from './components/TaskList';
import TaskForm from './components/TaskForm';
import StatsBar from './components/StatsBar';
import { taskService } from './services/taskService';
import './App.css';

function App() {
  const [tasks, setTasks]   = useState([]);
  const [stats, setStats]   = useState({ total: 0, completed: 0, pending: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);
  const [filter, setFilter] = useState('ALL'); // ALL | PENDING | COMPLETED

  const fetchTasks = useCallback(async () => {
    try {
      setLoading(true);
      const data = await taskService.getAll();
      setTasks(data);
      setError(null);
    } catch (err) {
      setError('Failed to load tasks. Is the API running?');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchStats = useCallback(async () => {
    try {
      const data = await taskService.getStats();
      setStats(data);
    } catch {
      // stats failure is non-critical
    }
  }, []);

  useEffect(() => {
    fetchTasks();
    fetchStats();
  }, [fetchTasks, fetchStats]);

  const handleCreate = async (taskData) => {
    const created = await taskService.create(taskData);
    setTasks(prev => [...prev, created]);
    fetchStats();
    return created;
  };

  const handleToggle = async (id) => {
    const updated = await taskService.toggle(id);
    setTasks(prev => prev.map(t => t.id === id ? updated : t));
    fetchStats();
  };

  const handleDelete = async (id) => {
    await taskService.delete(id);
    setTasks(prev => prev.filter(t => t.id !== id));
    fetchStats();
  };

  const filteredTasks = tasks.filter(t => {
    if (filter === 'PENDING')   return !t.completed;
    if (filter === 'COMPLETED') return t.completed;
    return true;
  });

  return (
    <div className="app">
      <header className="app-header">
        <h1>📋 Task Manager</h1>
        <p>Jenkins Practice App — Java + React + Python</p>
      </header>

      <main className="app-main">
        <StatsBar stats={stats} />

        <TaskForm onSubmit={handleCreate} />

        <div className="filter-bar">
          {['ALL', 'PENDING', 'COMPLETED'].map(f => (
            <button
              key={f}
              className={`filter-btn ${filter === f ? 'active' : ''}`}
              onClick={() => setFilter(f)}
            >
              {f}
            </button>
          ))}
        </div>

        {loading && <p className="loading">Loading tasks...</p>}
        {error   && <p className="error">{error}</p>}

        {!loading && !error && (
          <TaskList
            tasks={filteredTasks}
            onToggle={handleToggle}
            onDelete={handleDelete}
          />
        )}
      </main>
    </div>
  );
}

export default App;
