import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TaskList from './components/TaskList';

const sampleTasks = [
  { id: 1, title: 'Task One',   priority: 'HIGH',   completed: false, description: 'Desc 1' },
  { id: 2, title: 'Task Two',   priority: 'MEDIUM', completed: true,  description: '' },
  { id: 3, title: 'Task Three', priority: 'LOW',    completed: false, description: 'Desc 3' },
];

describe('TaskList Component', () => {
  const mockToggle = jest.fn();
  const mockDelete = jest.fn();

  beforeEach(() => {
    mockToggle.mockClear();
    mockDelete.mockClear();
  });

  test('renders all tasks', () => {
    render(<TaskList tasks={sampleTasks} onToggle={mockToggle} onDelete={mockDelete} />);
    expect(screen.getAllByTestId('task-item')).toHaveLength(3);
    expect(screen.getByText('Task One')).toBeInTheDocument();
    expect(screen.getByText('Task Two')).toBeInTheDocument();
  });

  test('shows empty state when no tasks', () => {
    render(<TaskList tasks={[]} onToggle={mockToggle} onDelete={mockDelete} />);
    expect(screen.getByText(/No tasks found/i)).toBeInTheDocument();
  });

  test('calls onToggle when checkbox clicked', () => {
    render(<TaskList tasks={sampleTasks} onToggle={mockToggle} onDelete={mockDelete} />);
    const checkboxes = screen.getAllByRole('checkbox');
    fireEvent.click(checkboxes[0]);
    expect(mockToggle).toHaveBeenCalledWith(1);
  });

  test('calls onDelete when delete button clicked', () => {
    render(<TaskList tasks={sampleTasks} onToggle={mockToggle} onDelete={mockDelete} />);
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    fireEvent.click(deleteButtons[0]);
    expect(mockDelete).toHaveBeenCalledWith(1);
  });

  test('renders priority correctly', () => {
    render(<TaskList tasks={sampleTasks} onToggle={mockToggle} onDelete={mockDelete} />);
    expect(screen.getByText('HIGH')).toBeInTheDocument();
    expect(screen.getByText('MEDIUM')).toBeInTheDocument();
    expect(screen.getByText('LOW')).toBeInTheDocument();
  });
});
