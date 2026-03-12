import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import App from './App';
import { taskService } from './services/taskService';

// Mock the taskService
jest.mock('./services/taskService');

const mockTasks = [
  { id: 1, title: 'Buy groceries',   description: 'Milk and eggs', priority: 'HIGH',   completed: false },
  { id: 2, title: 'Write tests',     description: '',              priority: 'MEDIUM', completed: true  },
  { id: 3, title: 'Read a book',     description: 'Clean Code',    priority: 'LOW',    completed: false },
];

const mockStats = { total: 3, completed: 1, pending: 2 };

beforeEach(() => {
  taskService.getAll.mockResolvedValue(mockTasks);
  taskService.getStats.mockResolvedValue(mockStats);
  taskService.create.mockImplementation(task =>
    Promise.resolve({ id: 99, ...task, completed: false })
  );
  taskService.toggle.mockImplementation(id => {
    const task = mockTasks.find(t => t.id === id);
    return Promise.resolve({ ...task, completed: !task.completed });
  });
  taskService.delete.mockResolvedValue({});
});

afterEach(() => jest.clearAllMocks());

describe('App Component', () => {
  test('renders header correctly', async () => {
    render(<App />);
    await waitFor(() => expect(taskService.getAll).toHaveBeenCalled());
    expect(screen.getByText(/Task Manager/i)).toBeInTheDocument();
  });

  test('displays tasks after loading', async () => {
    render(<App />);
    await waitFor(() => screen.getByTestId('task-list'));
    expect(screen.getByText('Buy groceries')).toBeInTheDocument();
    expect(screen.getByText('Write tests')).toBeInTheDocument();
    expect(screen.getByText('Read a book')).toBeInTheDocument();
  });

  test('shows stats bar with correct counts', async () => {
    render(<App />);
    await waitFor(() => screen.getByTestId('stats-bar'));
    expect(screen.getByText('3')).toBeInTheDocument(); // total
    expect(screen.getByText('1')).toBeInTheDocument(); // completed
    expect(screen.getByText('2')).toBeInTheDocument(); // pending
  });

  test('shows error message when API fails', async () => {
    taskService.getAll.mockRejectedValue(new Error('Network error'));
    render(<App />);
    await waitFor(() =>
      expect(screen.getByText(/Failed to load tasks/i)).toBeInTheDocument()
    );
  });
});

describe('TaskForm', () => {
  test('renders form with all fields', async () => {
    render(<App />);
    await waitFor(() => screen.getByTestId('task-form'));
    expect(screen.getByTestId('input-title')).toBeInTheDocument();
    expect(screen.getByTestId('input-priority')).toBeInTheDocument();
    expect(screen.getByTestId('input-description')).toBeInTheDocument();
  });

  test('creates a new task on form submit', async () => {
    const user = userEvent.setup();
    render(<App />);
    await waitFor(() => screen.getByTestId('task-form'));

    await user.type(screen.getByTestId('input-title'), 'New test task');
    await user.click(screen.getByText('+ Add Task'));

    await waitFor(() => expect(taskService.create).toHaveBeenCalledWith(
      expect.objectContaining({ title: 'New test task' })
    ));
  });

  test('shows validation error when title is empty', async () => {
    const user = userEvent.setup();
    render(<App />);
    await waitFor(() => screen.getByTestId('task-form'));

    await user.click(screen.getByText('+ Add Task'));
    expect(screen.getByText('Title is required')).toBeInTheDocument();
  });

  test('clears form after successful submission', async () => {
    const user = userEvent.setup();
    render(<App />);
    await waitFor(() => screen.getByTestId('task-form'));

    const titleInput = screen.getByTestId('input-title');
    await user.type(titleInput, 'Task to clear');
    await user.click(screen.getByText('+ Add Task'));

    await waitFor(() => expect(titleInput).toHaveValue(''));
  });
});

describe('Task Filters', () => {
  test('shows all tasks by default', async () => {
    render(<App />);
    await waitFor(() => screen.getByTestId('task-list'));
    expect(screen.getAllByTestId('task-item')).toHaveLength(3);
  });

  test('filters pending tasks correctly', async () => {
    const user = userEvent.setup();
    render(<App />);
    await waitFor(() => screen.getByTestId('task-list'));

    await user.click(screen.getByText('PENDING'));
    expect(screen.getAllByTestId('task-item')).toHaveLength(2);
  });

  test('filters completed tasks correctly', async () => {
    const user = userEvent.setup();
    render(<App />);
    await waitFor(() => screen.getByTestId('task-list'));

    await user.click(screen.getByText('COMPLETED'));
    expect(screen.getAllByTestId('task-item')).toHaveLength(1);
  });
});
