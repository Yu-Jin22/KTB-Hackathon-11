package com.example.eating.domain;

import com.example.eating.domain.Recipe;
import jakarta.persistence.*;
import lombok.Getter;

@Entity
@Getter
public class RecipeTip {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "recipe_id", nullable = false)
    private Recipe recipe;

    @Column(nullable = false)
    private String content;

    protected RecipeTip() {}

    public RecipeTip(Recipe recipe, String content) {
        this.recipe = recipe;
        this.content = content;
    }
}