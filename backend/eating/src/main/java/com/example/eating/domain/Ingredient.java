package com.example.eating.domain;

import com.example.eating.domain.Recipe;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Getter
@NoArgsConstructor
public class Ingredient {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "recipe_id", nullable = false)
    private Recipe recipe;

    private String name;
    private String amount;
    private String unit;

    @Column(length = 500)
    private String note;

    public Ingredient(Recipe recipe, String name, String amount, String unit, String note) {
        this.recipe = recipe;
        this.name = name;
        this.amount = amount;
        this.unit = unit;
        this.note = note;
    }
}