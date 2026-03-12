package com.devops.practice.service;

import com.devops.practice.model.Task;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

@DisplayName("TaskService Unit Tests")
class TaskServiceTest {

    private TaskService taskService;

    @BeforeEach
    void setUp() {
        taskService = new TaskService();
    }

    @Test
    @DisplayName("Should create a task with auto-generated ID")
    void createTask_ShouldAssignId() {
        Task task = Task.builder().title("Buy groceries").build();
        Task created = taskService.createTask(task);

        assertThat(created.getId()).isNotNull();
        assertThat(created.getTitle()).isEqualTo("Buy groceries");
        assertThat(created.getPriority()).isEqualTo("MEDIUM");
        assertThat(created.isCompleted()).isFalse();
    }

    @Test
    @DisplayName("Should return all created tasks")
    void getAllTasks_ShouldReturnAllTasks() {
        taskService.createTask(Task.builder().title("Task 1").build());
        taskService.createTask(Task.builder().title("Task 2").build());
        taskService.createTask(Task.builder().title("Task 3").build());

        List<Task> all = taskService.getAllTasks();
        assertThat(all).hasSize(3);
    }

    @Test
    @DisplayName("Should find task by ID")
    void getTaskById_ShouldReturnTask_WhenExists() {
        Task created = taskService.createTask(Task.builder().title("Find me").build());

        Optional<Task> found = taskService.getTaskById(created.getId());

        assertThat(found).isPresent();
        assertThat(found.get().getTitle()).isEqualTo("Find me");
    }

    @Test
    @DisplayName("Should return empty when task not found")
    void getTaskById_ShouldReturnEmpty_WhenNotExists() {
        Optional<Task> found = taskService.getTaskById(999L);
        assertThat(found).isEmpty();
    }

    @Test
    @DisplayName("Should toggle task completion status")
    void toggleComplete_ShouldFlipStatus() {
        Task created = taskService.createTask(Task.builder().title("Toggle me").build());
        assertThat(created.isCompleted()).isFalse();

        Optional<Task> toggled = taskService.toggleComplete(created.getId());
        assertThat(toggled).isPresent();
        assertThat(toggled.get().isCompleted()).isTrue();

        // Toggle back
        taskService.toggleComplete(created.getId());
        assertThat(taskService.getTaskById(created.getId()).get().isCompleted()).isFalse();
    }

    @Test
    @DisplayName("Should update task fields")
    void updateTask_ShouldUpdateAllFields() {
        Task original = taskService.createTask(Task.builder().title("Old title").build());
        Task updated = Task.builder()
                .title("New title")
                .description("Updated description")
                .priority("HIGH")
                .build();

        Optional<Task> result = taskService.updateTask(original.getId(), updated);

        assertThat(result).isPresent();
        assertThat(result.get().getTitle()).isEqualTo("New title");
        assertThat(result.get().getDescription()).isEqualTo("Updated description");
        assertThat(result.get().getPriority()).isEqualTo("HIGH");
        assertThat(result.get().getId()).isEqualTo(original.getId());
    }

    @Test
    @DisplayName("Should delete task successfully")
    void deleteTask_ShouldRemoveTask() {
        Task created = taskService.createTask(Task.builder().title("Delete me").build());

        boolean deleted = taskService.deleteTask(created.getId());

        assertThat(deleted).isTrue();
        assertThat(taskService.getTaskById(created.getId())).isEmpty();
    }

    @Test
    @DisplayName("Should return false when deleting non-existent task")
    void deleteTask_ShouldReturnFalse_WhenNotExists() {
        boolean deleted = taskService.deleteTask(9999L);
        assertThat(deleted).isFalse();
    }

    @Test
    @DisplayName("Should filter tasks by priority")
    void getTasksByPriority_ShouldReturnMatchingTasks() {
        taskService.createTask(Task.builder().title("Low 1").priority("LOW").build());
        taskService.createTask(Task.builder().title("High 1").priority("HIGH").build());
        taskService.createTask(Task.builder().title("High 2").priority("HIGH").build());

        List<Task> highPriority = taskService.getTasksByPriority("HIGH");

        assertThat(highPriority).hasSize(2);
        assertThat(highPriority).allMatch(t -> "HIGH".equals(t.getPriority()));
    }

    @Test
    @DisplayName("Should count completed and pending tasks correctly")
    void countStats_ShouldReturnCorrectCounts() {
        Task t1 = taskService.createTask(Task.builder().title("T1").build());
        Task t2 = taskService.createTask(Task.builder().title("T2").build());
        taskService.createTask(Task.builder().title("T3").build());

        taskService.toggleComplete(t1.getId());
        taskService.toggleComplete(t2.getId());

        assertThat(taskService.countCompleted()).isEqualTo(2);
        assertThat(taskService.countPending()).isEqualTo(1);
    }

    @Test
    @DisplayName("Should return empty list when no tasks match priority")
    void getTasksByPriority_ShouldReturnEmpty_WhenNoMatch() {
        taskService.createTask(Task.builder().title("Low task").priority("LOW").build());

        List<Task> critical = taskService.getTasksByPriority("CRITICAL");
        assertThat(critical).isEmpty();
    }
}
