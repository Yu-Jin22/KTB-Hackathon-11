package com.example.eating.domain;

import jakarta.persistence.*;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Getter
@NoArgsConstructor
public class RecipeStep {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private int stepNumber;

    @Column(columnDefinition = "TEXT")
    private String instruction;

    private double timestamp;

    private String duration;

    @Column(columnDefinition = "TEXT")
    private String details;

    @Column(columnDefinition = "TEXT")
    private String tips;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "recipe_id", nullable = false)
    private Recipe recipe;

    @Builder

    public RecipeStep(int stepNumber, String instruction, double timestamp, String duration, String details, String tips, Recipe recipe) {
        this.stepNumber = stepNumber;
        this.instruction = instruction;
        this.timestamp = timestamp;
        this.duration = duration;
        this.details = details;
        this.tips = tips;
        this.recipe = recipe;
    }
}