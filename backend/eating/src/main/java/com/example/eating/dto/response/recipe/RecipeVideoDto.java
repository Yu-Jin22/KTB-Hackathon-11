package com.example.eating.dto.response.recipe;

import com.example.eating.domain.RecipeVideo;
import lombok.Getter;

@Getter
public class RecipeVideoDto {

    private String videoId;
    private String title;
    private Integer duration;
    private String url;

    public static RecipeVideoDto from(RecipeVideo video) {
        if (video == null) {
            return null;
        }

        RecipeVideoDto dto = new RecipeVideoDto();
        dto.videoId = video.getVideoId();
        dto.title = video.getTitle();
        dto.duration = video.getDuration();
        dto.url = video.getUrl();
        return dto;
    }
}