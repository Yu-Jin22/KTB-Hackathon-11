package com.example.eating.domain;

import jakarta.persistence.*;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Getter
@NoArgsConstructor
public class Recipe {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** 레시피 소유자 */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    private String servings;
    private String totalTime;
    private String difficulty;

    @OneToMany(mappedBy = "recipe", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("stepNumber ASC")
    private List<RecipeStep> steps = new ArrayList<>();

    @OneToMany(mappedBy = "recipe", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Ingredient> ingredients = new ArrayList<>();

    @ElementCollection
    @CollectionTable(
            name = "recipe_tips",
            joinColumns = @JoinColumn(name = "recipe_id")
    )
    @Column(name = "tip")
    private List<String> tips = new ArrayList<>();

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;


    @Builder
    public Recipe(User user, String title, String description, String servings, String totalTime, String difficulty, List<RecipeStep> steps, List<Ingredient> ingredients, List<String> tips, LocalDateTime createdAt) {
        this.user = user;
        this.title = title;
        this.description = description;
        this.servings = servings;
        this.totalTime = totalTime;
        this.difficulty = difficulty;
        this.steps = steps;
        this.ingredients = ingredients;
        this.tips = tips;
        this.createdAt = createdAt;
    }
}