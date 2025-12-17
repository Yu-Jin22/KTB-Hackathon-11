package com.example.eating.repository;

import com.example.eating.domain.Recipe;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface RecipeRepository extends JpaRepository<Recipe, Long> {

    List<Recipe> findByUser_IdOrderByCreatedAtDesc(Long userId);
}
