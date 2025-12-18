package com.example.eating.dto.response.chat;

import lombok.Getter;

import java.util.Map;

@Getter
public class ChatResponse {

    private String reply;

    // step_info: Dict[str, Any]
    private Map<String, Object> step_info;

    // session_status: Dict[str, Any]
    private Map<String, Object> session_status;
}