package com.example.eating.dto.request.recipe;

import lombok.Getter;

import java.util.List;

@Getter
public class RecipeResultPayload {

    private String title;
    private String description;

    private String servings;
    private String totalTime;
    private String difficulty;

    private List<IngredientDto> ingredients;
    private List<RecipeStepDto> steps;

    private List<String> tips;
}