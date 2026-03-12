package com.devops.practice.controller;

import com.devops.practice.model.Task;
import com.devops.practice.service.TaskService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;
import java.util.Optional;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(TaskController.class)
@DisplayName("TaskController Integration Tests")
class TaskControllerTest {

    @Autowired MockMvc mockMvc;
    @Autowired ObjectMapper objectMapper;
    @MockBean  TaskService taskService;

    @Test
    @DisplayName("GET /api/tasks - returns list of tasks")
    void getAllTasks_ShouldReturn200() throws Exception {
        Task t = Task.builder().id(1L).title("Test task").priority("HIGH").build();
        when(taskService.getAllTasks()).thenReturn(List.of(t));

        mockMvc.perform(get("/api/tasks"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].title").value("Test task"))
                .andExpect(jsonPath("$[0].priority").value("HIGH"));
    }

    @Test
    @DisplayName("GET /api/tasks/{id} - returns task when found")
    void getTask_ShouldReturn200_WhenFound() throws Exception {
        Task t = Task.builder().id(1L).title("Found task").build();
        when(taskService.getTaskById(1L)).thenReturn(Optional.of(t));

        mockMvc.perform(get("/api/tasks/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.title").value("Found task"));
    }

    @Test
    @DisplayName("GET /api/tasks/{id} - returns 404 when not found")
    void getTask_ShouldReturn404_WhenNotFound() throws Exception {
        when(taskService.getTaskById(99L)).thenReturn(Optional.empty());

        mockMvc.perform(get("/api/tasks/99"))
                .andExpect(status().isNotFound());
    }

    @Test
    @DisplayName("POST /api/tasks - creates task and returns 201")
    void createTask_ShouldReturn201() throws Exception {
        Task input   = Task.builder().title("New task").build();
        Task created = Task.builder().id(1L).title("New task").priority("MEDIUM").build();
        when(taskService.createTask(any(Task.class))).thenReturn(created);

        mockMvc.perform(post("/api/tasks")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(input)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value(1))
                .andExpect(jsonPath("$.title").value("New task"));
    }

    @Test
    @DisplayName("POST /api/tasks - returns 400 when title is blank")
    void createTask_ShouldReturn400_WhenTitleBlank() throws Exception {
        Task invalid = Task.builder().title("").build();

        mockMvc.perform(post("/api/tasks")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(invalid)))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("PATCH /api/tasks/{id}/toggle - toggles completion")
    void toggleComplete_ShouldReturn200() throws Exception {
        Task toggled = Task.builder().id(1L).title("Task").completed(true).build();
        when(taskService.toggleComplete(1L)).thenReturn(Optional.of(toggled));

        mockMvc.perform(patch("/api/tasks/1/toggle"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.completed").value(true));
    }

    @Test
    @DisplayName("DELETE /api/tasks/{id} - returns 204 when deleted")
    void deleteTask_ShouldReturn204() throws Exception {
        when(taskService.deleteTask(1L)).thenReturn(true);

        mockMvc.perform(delete("/api/tasks/1"))
                .andExpect(status().isNoContent());
    }

    @Test
    @DisplayName("GET /health - returns UP status")
    void health_ShouldReturnUp() throws Exception {
        mockMvc.perform(get("/health"))
                .andExpect(status().isOk());
    }
}
