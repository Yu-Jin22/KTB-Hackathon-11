package com.example.eating.controller;

import com.example.eating.dto.request.recipe.RecipeExtractRequest;
import com.example.eating.dto.response.job.RecipeJobCreateResponse;
import com.example.eating.dto.response.job.RecipeJobStatusResponse;
import com.example.eating.dto.response.recipe.RecipeResponse;
import com.example.eating.service.RecipeJobService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/recipes")
public class RecipeAnalyzeController {

    private final RecipeJobService recipeJobService;

    @PostMapping("/analyze")
    public RecipeJobCreateResponse analyze(
            @RequestHeader("email") String email,
            @RequestBody RecipeExtractRequest request
    ) {
        return recipeJobService.startAnalyze(email, request);
    }

    @GetMapping("/status/{jobId}")
    public RecipeJobStatusResponse getStatus(
            @RequestHeader("email") String email,
            @PathVariable String jobId
    ) {
        return recipeJobService.getStatus(email, jobId);
    }

    @GetMapping("/result/{jobId}")
    public RecipeResponse getResult(
            @RequestHeader("email") String email,
            @PathVariable String jobId
    ) {
        return recipeJobService.getResultAndSave(email, jobId);
    }


}