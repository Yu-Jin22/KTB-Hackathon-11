package com.example.eating.dto.response.recipe;

import com.example.eating.domain.Ingredient;
import lombok.Getter;

@Getter
public class IngredientDto {

    private String name;
    private String amount;
    private String unit;
    private String note;

    public static IngredientDto from(Ingredient ingredient) {
        IngredientDto dto = new IngredientDto();
        dto.name = ingredient.getName();
        dto.amount = ingredient.getAmount();
        dto.unit = ingredient.getUnit();
        dto.note = ingredient.getNote();
        return dto;
    }
}