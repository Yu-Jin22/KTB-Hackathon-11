package com.example.eating.dto.request.chat;

import lombok.Getter;

import java.util.Map;

@Getter
public class StartSessionRequest {

    private String session_id;
    // FastAPI: recipe: Dict[str, Any]
    private Map<String, Object> recipe;

    public StartSessionRequest(String session_id, Map<String, Object> recipe) {
        this.session_id = session_id;
        this.recipe = recipe;
    }
}