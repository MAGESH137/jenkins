package com.devops.practice.service;

import com.devops.practice.model.Task;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

@Service
public class TaskService {

    private final ConcurrentHashMap<Long, Task> tasks = new ConcurrentHashMap<>();
    private final AtomicLong idCounter = new AtomicLong(1);

    public List<Task> getAllTasks() {
        return new ArrayList<>(tasks.values());
    }

    public Optional<Task> getTaskById(Long id) {
        return Optional.ofNullable(tasks.get(id));
    }

    public Task createTask(Task task) {
        long id = idCounter.getAndIncrement();
        task.setId(id);
        if (task.getPriority() == null) {
            task.setPriority("MEDIUM");
        }
        tasks.put(id, task);
        return task;
    }

    public Optional<Task> updateTask(Long id, Task updated) {
        if (!tasks.containsKey(id)) {
            return Optional.empty();
        }
        updated.setId(id);
        tasks.put(id, updated);
        return Optional.of(updated);
    }

    public Optional<Task> toggleComplete(Long id) {
        Task task = tasks.get(id);
        if (task == null) return Optional.empty();
        task.setCompleted(!task.isCompleted());
        return Optional.of(task);
    }

    public boolean deleteTask(Long id) {
        return tasks.remove(id) != null;
    }

    public List<Task> getTasksByPriority(String priority) {
        return tasks.values().stream()
                .filter(t -> priority.equalsIgnoreCase(t.getPriority()))
                .toList();
    }

    public long countCompleted() {
        return tasks.values().stream().filter(Task::isCompleted).count();
    }

    public long countPending() {
        return tasks.values().stream().filter(t -> !t.isCompleted()).count();
    }
}
