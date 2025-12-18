package com.example.eating.dto.response.recipe;

import com.example.eating.domain.Recipe;
import com.example.eating.domain.RecipeTip;
import lombok.Builder;
import lombok.Getter;

import java.util.List;
import java.util.stream.Collectors;

@Getter
@Builder
public class RecipeResponse {

    private Long recipeId;
    private String title;
    private String description;
    private String servings;
    private String total_time;
    private String difficulty;

    private RecipeVideoDto video_info;

    private List<IngredientDto> ingredients;
    private List<RecipeStepDto> steps;
    private List<String> tips;

    public static RecipeResponse from(Recipe recipe) {
        return RecipeResponse.builder()
                .recipeId(recipe.getId())
                .title(recipe.getTitle())
                .description(recipe.getDescription())
                .servings(recipe.getServings())
                .total_time(recipe.getTotalTime())
                .difficulty(recipe.getDifficulty())

                .ingredients(
                        recipe.getIngredients().stream()
                                .map(IngredientDto::from)
                                .collect(Collectors.toList())
                )
                .steps(
                        recipe.getSteps().stream()
                                .map(RecipeStepDto::from)
                                .collect(Collectors.toList())
                )
                .tips(
                        recipe.getTips().stream()
                                .map(RecipeTip::getContent)
                                .collect(Collectors.toList())
                )
                .video_info(RecipeVideoDto.from(recipe.getRecipeVideo()))
                .build();
    }
}