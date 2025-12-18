package com.example.eating.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.eating.dto.request.sse.JobProgressRequest;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/internal/jobs")
@RequiredArgsConstructor
public class InternalJobProgressController {
    private final SseController sseController;

    @PostMapping("/{jobId}/progress")
    public ResponseEntity<Void> onProgress(
            @PathVariable String jobId, @RequestBody JobProgressRequest request) {

        if (request.getJobId() == null || request.getJobId().isBlank()) {

        }

        sseController.sendToJob(jobId, jobId, request);

        if ("complete".equalsIgnoreCase(request.getStatus())) {
            sseController.sendToJob(jobId, "complete", request);
            sseController.completeJob(jobId);
        } else if ("failed".equalsIgnoreCase(request.getStatus())) {
            sseController.sendToJob(jobId, "failed", request);
            sseController.completeJob(jobId);
        }

        return ResponseEntity.ok().build();
    }
}
