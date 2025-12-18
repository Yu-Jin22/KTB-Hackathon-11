package com.example.eating.dto.response.chat;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.util.List;

@Getter
@AllArgsConstructor
public class SessionStatus {

    private String session_id;
    private String recipe_title;
    private int current_step;
    private int total_steps;
    private List<Integer> completed_steps;
    private int progress_percent;
}