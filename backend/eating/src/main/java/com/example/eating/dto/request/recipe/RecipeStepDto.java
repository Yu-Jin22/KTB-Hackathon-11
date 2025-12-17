package com.example.eating.dto.request.recipe;

import lombok.Getter;

@Getter
public class RecipeStepDto {

    private int stepNumber;

    private String instruction;

    private double timestamp;

    private String duration;

    private String details;
    private String tips;

    private String imageUrl;
}