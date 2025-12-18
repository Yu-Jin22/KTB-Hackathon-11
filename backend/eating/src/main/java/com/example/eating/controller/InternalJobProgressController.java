package com.example.eating.controller;

import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.eating.dto.request.sse.JobProgressRequest;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@RestController
@RequestMapping("/internal/jobs")
@RequiredArgsConstructor
public class InternalJobProgressController {
    private final SseController sseController;

    @PostMapping("/{jobId}/progress")
    public ResponseEntity<Void> onProgress(
            @PathVariable String jobId, @RequestBody JobProgressRequest request) {
        log.info(
                "event=job_progress_recevied method=POST path=/internal/jobs/{jobId}/progress jobId={} status={} progress={} step={}",
                jobId,
                request.getStatus(),
                request.getProgress(),
                request.getStep());

        sseController.sendToJob(jobId, "progress", request);

        if ("completed".equalsIgnoreCase(request.getStatus())) {
            log.info(
                    "event=job_progress_completed jobId={} status={} progress={} step={}",
                    jobId,
                    request.getStatus(),
                    request.getProgress(),
                    request.getStep());
            sseController.sendToJob(jobId, "completed", request);
            sseController.completeJob(jobId);
        } else if ("failed".equalsIgnoreCase(request.getStatus())) {
            log.warn("event=job_failed_received jobId={} progress={} step={} message={}",
                    jobId, request.getProgress(), request.getStep(), request.getMessage());
            sseController.sendToJob(jobId, "failed", request);
            sseController.completeJob(jobId);
        }

        return ResponseEntity.ok().build();
    }
}
