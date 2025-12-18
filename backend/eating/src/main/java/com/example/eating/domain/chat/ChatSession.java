package com.example.eating.domain.chat;

import jakarta.persistence.*;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(
        name = "chat_session",
        indexes = {
                @Index(name = "idx_chat_session_user", columnList = "user_id"),
                @Index(name = "idx_chat_session_status", columnList = "status")
        }
)
@Getter
@Setter
@NoArgsConstructor
public class ChatSession {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * FastAPI와 공유되는 세션 ID
     */
    @Column(name = "session_id", nullable = false, unique = true, length = 64)
    private String sessionId;

    /**
     * 세션 소유자
     */
    @Column(name = "user_id", nullable = false)
    private Long userId;

    /**
     * 레시피 제목 (조회 최적화용)
     */
    @Column(name = "recipe_title", nullable = false)
    private String recipeTitle;

    /**
     * 현재 단계
     */
    @Column(name = "current_step", nullable = false)
    private int currentStep;

    /**
     * 전체 단계 수
     */
    @Column(name = "total_steps", nullable = false)
    private int totalSteps;

    /**
     * 완료된 단계 목록
     */
    @ElementCollection
    @CollectionTable(
            name = "chat_session_completed_step",
            joinColumns = @JoinColumn(name = "chat_session_id")
    )
    @Column(name = "step_number")
    private List<Integer> completedSteps = new ArrayList<>();

    /**
     * 세션 상태
     */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ChatSessionStatus status;

    /**
     * 생성 시간
     */
    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    /**
     * 마지막 사용 시간 (만료 판단용)
     */
    @Column(name = "last_used_at", nullable = false)
    private LocalDateTime lastUsedAt;


    @Builder
    public ChatSession(
            String sessionId,
            Long userId,
            String recipeTitle,
            int totalSteps
    ) {
        this.sessionId = sessionId;
        this.userId = userId;
        this.recipeTitle = recipeTitle;
        this.totalSteps = totalSteps;
        this.currentStep = 1;
        this.status = ChatSessionStatus.ACTIVE;
        this.createdAt = LocalDateTime.now();
        this.lastUsedAt = LocalDateTime.now();
    }

    /* ================== 도메인 로직 ================== */

    public void markStepCompleted(int stepNumber) {
        if (!completedSteps.contains(stepNumber)) {
            completedSteps.add(stepNumber);
        }

        if (stepNumber < totalSteps) {
            this.currentStep = stepNumber + 1;
        } else {
            this.status = ChatSessionStatus.FINISHED;
        }

        touch();
    }

    public void expire() {
        this.status = ChatSessionStatus.EXPIRED;
        touch();
    }

    public void touch() {
        this.lastUsedAt = LocalDateTime.now();
    }

    public int calculateProgress() {
        if (totalSteps == 0) return 0;
        return (int) ((completedSteps.size() * 100.0) / totalSteps);
    }
}