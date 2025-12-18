package com.example.eating.repository.chat;

import com.example.eating.domain.chat.ChatSession;
import com.example.eating.domain.chat.ChatSessionStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public interface ChatSessionRepository extends JpaRepository<ChatSession, Long> {

    /**
     * sessionId로 세션 조회 (FastAPI 연동 핵심)
     */
    Optional<ChatSession> findBySessionId(String sessionId);

    /**
     * 사용자별 활성 세션 조회
     * - 한 유저가 동시에 여러 세션을 가질 수 있게 설계
     */
    List<ChatSession> findByUserIdAndStatus(
            Long userId,
            ChatSessionStatus status
    );

    /**
     * 사용자별 세션 목록 (최근 사용순)
     * - 마이페이지 / 최근 요리 세션용
     */
    List<ChatSession> findByUserIdOrderByLastUsedAtDesc(Long userId);

    /**
     * 만료 대상 세션 조회
     * - 스케줄러에서 사용
     */
    List<ChatSession> findByStatusAndLastUsedAtBefore(
            ChatSessionStatus status,
            LocalDateTime expiredBefore
    );
}