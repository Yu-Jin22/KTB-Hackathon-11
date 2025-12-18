package com.example.eating.dto.request.sse;

import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class JobProgressRequest {
    private String jobId;
    private String status;
    private int progress;
    private String message;
}