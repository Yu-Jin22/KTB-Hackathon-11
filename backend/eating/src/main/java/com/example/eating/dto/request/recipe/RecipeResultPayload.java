package com.example.eating.dto.request.recipe;

import com.example.eating.dto.response.recipe.IngredientDto;
import com.example.eating.dto.response.recipe.RecipeStepDto;
import lombok.Getter;

import java.util.List;

@Getter
public class RecipeResultPayload {

    private boolean success;
    private double elapsedTime;
    private int inputSegmentsCount;
    private RecipeDto recipe;
    private VideoInfoDto video_info;

    @Getter
    public static class RecipeDto {
        private String title;
        private String description;
        private String servings;
        private String total_time;
        private String difficulty;
        private List<IngredientDto> ingredients;
        private List<RecipeStepDto> steps;
        private List<String> tips;
    }

    @Getter
    public static class VideoInfoDto {
        private String video_id;
        private String title;
        private Integer duration;
        private String url;
    }
}