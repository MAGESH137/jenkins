import React, { useState } from 'react';

function TaskForm({ onSubmit }) {
  const [title, setTitle]       = useState('');
  const [description, setDesc]  = useState('');
  const [priority, setPriority] = useState('MEDIUM');
  const [submitting, setSub]    = useState(false);
  const [error, setError]       = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('Title is required');
      return;
    }
    try {
      setSub(true);
      setError('');
      await onSubmit({ title: title.trim(), description: description.trim(), priority });
      setTitle('');
      setDesc('');
      setPriority('MEDIUM');
    } catch {
      setError('Failed to create task. Please try again.');
    } finally {
      setSub(false);
    }
  };

  return (
    <form className="task-form" onSubmit={handleSubmit} data-testid="task-form">
      <h2>Add New Task</h2>

      {error && <p className="form-error">{error}</p>}

      <div className="form-row">
        <input
          type="text"
          placeholder="Task title *"
          value={title}
          onChange={e => setTitle(e.target.value)}
          className="input-title"
          data-testid="input-title"
          maxLength={100}
        />
        <select
          value={priority}
          onChange={e => setPriority(e.target.value)}
          className="input-priority"
          data-testid="input-priority"
        >
          <option value="LOW">🟢 Low</option>
          <option value="MEDIUM">🟡 Medium</option>
          <option value="HIGH">🔴 High</option>
        </select>
      </div>

      <textarea
        placeholder="Description (optional)"
        value={description}
        onChange={e => setDesc(e.target.value)}
        className="input-description"
        data-testid="input-description"
        maxLength={500}
        rows={2}
      />

      <button type="submit" disabled={submitting} className="submit-btn">
        {submitting ? 'Adding...' : '+ Add Task'}
      </button>
    </form>
  );
}

export default TaskForm;
