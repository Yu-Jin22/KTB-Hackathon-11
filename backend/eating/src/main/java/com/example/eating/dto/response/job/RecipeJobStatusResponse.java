package com.example.eating.dto.response.job;

import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class RecipeJobStatusResponse {

    private String jobId;

    private String status;
}