package com.example.eating.service;

import com.example.eating.dto.request.recipe.RecipeExtractRequest;
import com.example.eating.dto.response.job.RecipeJobCreateResponse;
import com.example.eating.dto.response.job.RecipeJobStatusResponse;
import com.example.eating.dto.response.recipe.RecipeResponse;
import com.example.eating.dto.request.recipe.RecipeResultPayload;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class RecipeJobService {

    private final WebClient fastApiClient;
    private final RecipeService recipeService;

    public RecipeJobCreateResponse startAnalyze(
            String email,
            RecipeExtractRequest request
    ) {
        Map<String, Object> response =
                fastApiClient.post()
                        .uri("/api/analyze")
                        .header("email", email)
                        .bodyValue(request)
                        .retrieve()
                        .bodyToMono(Map.class)
                        .block();

        return RecipeJobCreateResponse.builder()
                .jobId((String) response.get("job_id"))
                .status((String) response.get("status"))
                .build();
    }

    public RecipeJobStatusResponse getStatus(
            String userKey,
            String jobId
    ) {
        Map<String, Object> response =
                fastApiClient.get()
                        .uri("/api/status/{jobId}", jobId)
                        .header("X-USER-KEY", userKey)
                        .retrieve()
                        .bodyToMono(Map.class)
                        .block();

        return RecipeJobStatusResponse.builder()
                .jobId(jobId)
                .status((String) response.get("status"))
                .build();
    }

    public RecipeResponse getResultAndSave(
            String email,
            String jobId
    ) {
        RecipeResultPayload payload =
                fastApiClient.get()
                        .uri("/api/result/{jobId}", jobId)
                        .header("email", email)
                        .retrieve()
                        .bodyToMono(RecipeResultPayload.class)
                        .block();

        if (payload == null || payload.getRecipe() == null) {
            throw new IllegalStateException("Recipe result is empty");
        }

        return RecipeResponse.from(
                recipeService.saveRecipeResult(email, payload)
        );
    }
}