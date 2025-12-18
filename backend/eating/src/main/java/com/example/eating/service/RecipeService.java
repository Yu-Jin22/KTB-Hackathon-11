package com.example.eating.service;

import com.example.eating.domain.*;
import com.example.eating.dto.request.recipe.RecipeResultPayload;
import com.example.eating.repository.RecipeRepository;
import com.example.eating.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
public class RecipeService {

    private final UserRepository userRepository;
    private final RecipeRepository recipeRepository;

    @Transactional
    public Recipe saveRecipeResult(
            String email,
            RecipeResultPayload payload
    ) {
        User user = userRepository.findByEmail(email).orElseThrow(
                () -> new RuntimeException("")
        );

        // 1️⃣ Recipe 생성
        Recipe recipe = new Recipe(user);

        RecipeResultPayload.RecipeDto r = payload.getRecipe();
        recipe.setTitle(r.getTitle());
        recipe.setDescription(r.getDescription());
        recipe.setServings(r.getServings());
        recipe.setTotalTime(r.getTotal_time());
        recipe.setDifficulty(r.getDifficulty());

        // 2️⃣ Ingredients
        r.getIngredients().forEach(i ->
                recipe.addIngredient(
                        new Ingredient(
                                recipe,
                                i.getName(),
                                i.getAmount(),
                                i.getUnit(),
                                i.getNote()
                        )
                )
        );

        // 3️⃣ Steps
        r.getSteps().forEach(s ->
                recipe.addStep(
                        new RecipeStep(
                                s.getStep_number(),
                                s.getInstruction(),
                                s.getTimestamp(),
                                s.getDuration(),
                                s.getDetails(),
                                s.getTips(),
                                recipe
                        )
                )
        );

        // 4️⃣ Tips
        if (r.getTips() != null) {
            r.getTips().forEach(recipe::addTip);
        }

        // ✅ 핵심 1: Recipe 먼저 저장 (ID 확보)
        recipeRepository.saveAndFlush(recipe);

        log.info("video: {}", payload.getVideo_info());

        if (payload.getVideo_info() != null) {
            RecipeResultPayload.VideoInfoDto v = payload.getVideo_info();

            RecipeVideo video = new RecipeVideo(
                    recipe,
                    v.getVideo_id(),
                    v.getTitle(),
                    v.getDuration(),
                    v.getUrl()
            );

            recipe.setRecipeVideo(video); // cascade로 자동 저장
        }

        // ✅ 마지막 save
        return recipeRepository.save(recipe);
    }
}