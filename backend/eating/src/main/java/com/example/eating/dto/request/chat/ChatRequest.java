package com.example.eating.dto.request.chat;

import lombok.Getter;

@Getter
public class ChatRequest {

    private String session_id;
    private int step_number;
    private String message;
    private String image_base64; // Optional
}