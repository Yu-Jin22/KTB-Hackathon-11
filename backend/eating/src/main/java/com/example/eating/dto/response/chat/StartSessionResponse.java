package com.example.eating.dto.response.chat;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class StartSessionResponse {

    private String session_id;
    private String message;
    private int total_steps;
}