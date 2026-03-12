import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

export const taskService = {
  getAll:    ()            => api.get('/tasks').then(r => r.data),
  getById:   (id)          => api.get(`/tasks/${id}`).then(r => r.data),
  create:    (task)        => api.post('/tasks', task).then(r => r.data),
  update:    (id, task)    => api.put(`/tasks/${id}`, task).then(r => r.data),
  toggle:    (id)          => api.patch(`/tasks/${id}/toggle`).then(r => r.data),
  delete:    (id)          => api.delete(`/tasks/${id}`),
  getStats:  ()            => api.get('/tasks/stats').then(r => r.data),
  getByPriority: (priority) => api.get(`/tasks?priority=${priority}`).then(r => r.data),
};

export default taskService;
