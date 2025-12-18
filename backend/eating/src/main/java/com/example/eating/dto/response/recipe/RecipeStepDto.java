package com.example.eating.dto.response.recipe;

import com.example.eating.domain.RecipeStep;
import lombok.Getter;

@Getter
public class RecipeStepDto {

    private int step_number;
    private String instruction;
    private double timestamp;
    private String duration;
    private String details;
    private String tips;

    public static RecipeStepDto from(RecipeStep step) {
        RecipeStepDto dto = new RecipeStepDto();
        dto.step_number = step.getStepNumber();
        dto.instruction = step.getInstruction();
        dto.timestamp = step.getTimestamp();
        dto.duration = step.getDuration();
        dto.details = step.getDetails();
        dto.tips = step.getTips();
        return dto;
    }
}