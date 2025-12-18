package com.example.eating.dto.request.sse;

import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class JobProgressRequest {
    private String status;
    private Integer progress;
    private String step;
    private String message;
}