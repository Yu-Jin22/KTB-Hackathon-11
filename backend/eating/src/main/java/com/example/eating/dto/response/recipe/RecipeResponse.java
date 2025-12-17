package com.example.eating.dto.response.recipe;

import com.example.eating.dto.request.recipe.IngredientDto;
import com.example.eating.dto.request.recipe.RecipeStepDto;
import lombok.Builder;
import lombok.Getter;

import java.util.List;

@Getter
@Builder
public class RecipeResponse {

    private Long recipeId;

    private String title;
    private String description;

    private String servings;
    private String totalTime;
    private String difficulty;

    private List<IngredientDto> ingredients;
    private List<RecipeStepDto> steps;

    private List<String> tips;
}