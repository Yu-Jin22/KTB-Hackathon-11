package com.example.eating.controller.chat;

import com.example.eating.dto.request.chat.ChatRequest;
import com.example.eating.dto.request.chat.StartSessionRequest;
import com.example.eating.dto.response.chat.ChatResponse;
import com.example.eating.dto.response.chat.SessionStatus;
import com.example.eating.dto.response.chat.StartSessionResponse;
import com.example.eating.service.chat.ChatService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequiredArgsConstructor
@RequestMapping("/chat")
public class ChatController {

    private final ChatService chatService;

    @PostMapping("/start")
    public StartSessionResponse startSession(
            @RequestHeader("email") String email,
            @RequestBody StartSessionRequest request
    ) {
        return chatService.startSession(email, request);
    }

    @GetMapping("/session/{sessionId}")
    public SessionStatus getSessionStatus(
            @RequestHeader("email") String email,
            @PathVariable String sessionId
    ) {
        return chatService.getSessionStatus(email, sessionId);
    }

    @PostMapping("/message")
    public ChatResponse sendMessage(
            @RequestHeader("email") String email,
            @RequestBody ChatRequest request
    ) {
        return chatService.sendMessage(email, request);
    }

    @PostMapping("/session/{sessionId}/complete-step/{stepNumber}")
    public Map<String, Object> completeStep(
            @RequestHeader("email") String email,
            @PathVariable String sessionId,
            @PathVariable int stepNumber
    ) {
        return chatService.completeStep(email, sessionId, stepNumber);
    }

    @GetMapping("/session/{sessionId}/history")
    public Map<String, Object> getHistory(
            @RequestHeader("email") String email,
            @PathVariable String sessionId
    ) {
        return chatService.getHistory(email, sessionId);
    }

    @DeleteMapping("/session/{sessionId}")
    public Map<String, Object> endSession(
            @RequestHeader("email") String email,
            @PathVariable String sessionId
    ) {
        return chatService.endSession(email, sessionId);
    }
}
