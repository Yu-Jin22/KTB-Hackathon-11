package com.example.eating.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@Entity
public class RecipeVideo {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "recipe_id", nullable = false)
    private Recipe recipe;

    @Column(nullable = false)
    private String videoId;

    private String title;

    private Integer duration;

    @Column(length = 500)
    private String url;

    public RecipeVideo(
            Recipe recipe,
            String videoId,
            String title,
            Integer duration,
            String url
    ) {
        this.recipe = recipe;
        this.videoId = videoId;
        this.title = title;
        this.duration = duration;
        this.url = url;
    }
}