package com.example.eating.dto.response.recipe;

import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
public class RecipeListItemResponse {

    private Long recipeId;
    private String title;
    private String difficulty;
    private String totalTime;

    private LocalDateTime createdAt;
}