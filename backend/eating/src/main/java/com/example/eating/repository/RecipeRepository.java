package com.example.eating.repository;

import com.example.eating.domain.Recipe;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface RecipeRepository extends JpaRepository<Recipe, Long> {

    List<Recipe> findByUser_IdOrderByCreatedAtDesc(Long userId);

    // n+1 방지 단일 조회 메서드 아직 사용 x
    @EntityGraph(attributePaths = {
            "ingredients",
            "steps",
            "tips",
            "recipeVideo"
    })
    Optional<Recipe> findById(Long id);
}
