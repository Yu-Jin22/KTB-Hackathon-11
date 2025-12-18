package com.example.eating.service.chat;

import com.example.eating.domain.chat.ChatSession;
import com.example.eating.domain.chat.ChatSessionStatus;
import com.example.eating.domain.User;
import com.example.eating.dto.request.chat.ChatRequest;
import com.example.eating.dto.request.chat.StartSessionRequest;
import com.example.eating.dto.response.chat.ChatResponse;
import com.example.eating.dto.response.chat.SessionStatus;
import com.example.eating.dto.response.chat.StartSessionResponse;
import com.example.eating.repository.chat.ChatSessionRepository;
import com.example.eating.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Transactional
public class ChatService {

    private final ChatSessionRepository chatSessionRepository;
    private final UserRepository userRepository;
    private final WebClient fastApiClient;

    public StartSessionResponse startSession(
            String email,
            StartSessionRequest request
    ) {
        // 1️⃣ email → userId
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 사용자입니다."));
        Long userId = user.getId();

        // 2️⃣ Spring이 session_id 생성 (단일 기준)
        String sessionId = UUID.randomUUID().toString();

        // 3️⃣ recipe 파싱
        Map<String, Object> recipe = request.getRecipe();
        String recipeTitle = (String) recipe.getOrDefault("title", "요리");

        List<?> steps = (List<?>) recipe.getOrDefault("steps", List.of());
        int totalSteps = steps.size();

        // 4️⃣ DB 세션 생성
        ChatSession session = ChatSession.builder()
                .sessionId(sessionId)
                .userId(userId)
                .recipeTitle(recipeTitle)
                .totalSteps(totalSteps)
                .build();

        chatSessionRepository.save(session);

        // ✅ 5️⃣ FastAPI 전용 요청 DTO 생성 (핵심)
        StartSessionRequest fastApiRequest =
                new StartSessionRequest(sessionId, recipe);

        StartSessionResponse fastApiResponse =
                fastApiClient.post()
                        .uri("/api/chat/start")
                        .bodyValue(fastApiRequest)
                        .retrieve()
                        .bodyToMono(StartSessionResponse.class)
                        .block();

        // 6️⃣ Spring 기준 응답 반환
        return new StartSessionResponse(
                sessionId,                      // ⭐ Spring session_id
                fastApiResponse.getMessage(),   // FastAPI 메시지
                totalSteps
        );
    }

    @Transactional(readOnly = true)
    public SessionStatus getSessionStatus(
            String email,
            String sessionId
    ) {
        ChatSession session = getOwnedSession(email, sessionId);

        return new SessionStatus(
                session.getSessionId(),
                session.getRecipeTitle(),
                session.getCurrentStep(),
                session.getTotalSteps(),
                session.getCompletedSteps(),
                session.calculateProgress()
        );
    }


    public ChatResponse sendMessage(
            String email,
            ChatRequest request
    ) {
        ChatSession session = getOwnedSession(email, request.getSession_id());

        ChatResponse response =
                fastApiClient.post()
                        .uri("/api/chat/message")
                        .bodyValue(request)
                        .retrieve()
                        .bodyToMono(ChatResponse.class)
                        .block();

        // current_step 동기화
        Object currentStepObj = response.getSession_status().get("current_step");
        if (currentStepObj instanceof Number) {
            session.setCurrentStep(((Number) currentStepObj).intValue());
        }

        session.touch();
        return response;
    }


    public Map<String, Object> completeStep(
            String email,
            String sessionId,
            int stepNumber
    ) {
        ChatSession session = getOwnedSession(email, sessionId);

        Map<String, Object> response =
                fastApiClient.post()
                        .uri("/api/chat/session/{sessionId}/complete-step/{step}",
                                sessionId, stepNumber)
                        .retrieve()
                        .bodyToMono(Map.class)
                        .block();

        session.markStepCompleted(stepNumber);

        if (Boolean.TRUE.equals(response.get("is_finished"))) {
            session.setStatus(ChatSessionStatus.FINISHED);
        }

        return response;
    }


    @Transactional(readOnly = true)
    public Map<String, Object> getHistory(
            String email,
            String sessionId
    ) {
        getOwnedSession(email, sessionId);

        return fastApiClient.get()
                .uri("/api/chat/session/{sessionId}/history", sessionId)
                .retrieve()
                .bodyToMono(Map.class)
                .block();
    }


    public Map<String, Object> endSession(
            String email,
            String sessionId
    ) {
        ChatSession session = getOwnedSession(email, sessionId);

        Map<String, Object> response =
                fastApiClient.delete()
                        .uri("/api/chat/session/{sessionId}", sessionId)
                        .retrieve()
                        .bodyToMono(Map.class)
                        .block();

        session.setStatus(ChatSessionStatus.FINISHED);
        session.touch();

        return response;
    }


    private ChatSession getOwnedSession(String email, String sessionId) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 사용자입니다."));

        ChatSession session = chatSessionRepository.findBySessionId(sessionId)
                .orElseThrow(() -> new IllegalArgumentException("세션이 존재하지 않습니다."));

        if (!session.getUserId().equals(user.getId())) {
            throw new IllegalStateException("세션 접근 권한이 없습니다.");
        }

        return session;
    }
}
