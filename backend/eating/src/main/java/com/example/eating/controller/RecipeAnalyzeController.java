package com.example.eating.controller;

import com.example.eating.APIResponse;
import com.example.eating.dto.request.recipe.RecipeExtractRequest;
import com.example.eating.dto.response.job.RecipeJobCreateResponse;
import com.example.eating.dto.response.job.RecipeJobStatusResponse;
import com.example.eating.dto.response.recipe.RecipeResponse;
import com.example.eating.service.RecipeJobService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/recipes")
public class RecipeAnalyzeController {

    private final RecipeJobService recipeJobService;

    @PostMapping("/analyze")
    public RecipeJobCreateResponse analyze(
            @RequestHeader("email") String email,
            @RequestBody RecipeExtractRequest request) {
        log.info("event=recipe_extract_request Method=POST path=/recipes/analyze url={}", request.getUrl());
        return recipeJobService.startAnalyze(email, request);
    }

    @GetMapping("/status/{jobId}")
    public RecipeJobStatusResponse getStatus(
            @RequestHeader("email") String email,
            @PathVariable String jobId) {
        log.info("event=recipe_job_status Method=GET path=/recipes/status/{jobId} jobId={}", jobId);
        return recipeJobService.getStatus(email, jobId);
    }

    @GetMapping("/result/{jobId}")
    public APIResponse<RecipeResponse> getResult(
            @RequestHeader("email") String email,
            @PathVariable String jobId) {
        log.info("event=extrated_recipe_result Method=GET path=/recipes/result/{jobId} jobId={}", jobId);
        return APIResponse.success("", recipeJobService.getResultAndSave(email, jobId));
    }

}
