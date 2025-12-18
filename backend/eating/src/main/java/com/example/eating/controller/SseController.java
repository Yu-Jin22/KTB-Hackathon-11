package com.example.eating.controller;

import java.io.IOException;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.time.Instant;

import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

/**
 * SSE Hub
 * - FE: GET /api/sse/jobs/{jobId} 로 구독
 * - 내부(서비스/컨트롤러): sendToJob(jobId, "progress", payload) 로 이벤트 푸시
 */
@RestController
@RequestMapping("/sse")
public class SseController {

    /**
     * jobId -> (subscriberId -> emitter)
     */
    private final Map<String, Map<String, SseEmitter>> emittersByJob = new ConcurrentHashMap<>();

    /**
     * FE 구독 엔드포인트
     * - 브라우저 EventSource가 호출
     */
    @GetMapping(value = "/jobs/{jobId}", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter subcribeJob(@PathVariable String jobId) throws IOException {

        SseEmitter emitter = new SseEmitter(0L); // 타임아웃 없음
        String subscriberId = UUID.randomUUID().toString();

        emittersByJob
                .computeIfAbsent(jobId, k -> new ConcurrentHashMap<>())
                .put(subscriberId, emitter);

        // 최초 연결 확인용 이벤트
        emitter.send(SseEmitter.event()
                .name("connected")
                .data(Map.of(
                        "jobId", jobId,
                        "subscriberId", subscriberId,
                        "timestamp", Instant.now().toString())));

        // 연결 종료 / 에러 / 타임아웃 시 정리
        Runnable cleanup = () -> removeEmitter(jobId, subscriberId);
        emitter.onCompletion(cleanup);
        emitter.onTimeout(cleanup);
        emitter.onError(e -> removeEmitter(jobId, subscriberId));

        return emitter;
    }

    /**
     * 해당 jobId를 구독 중인 모든 클라이언트에게 이벤트 전송
     * eventName 예: progress, completed, failed, ping ...
     */
    public void sendToJob(String jobId, String eventName, Object data) {
        Map<String, SseEmitter> subs = emittersByJob.get(jobId);
        if (subs == null || subs.isEmpty())
            return;

        subs.forEach((sid, emitter) -> {
            try {
                emitter.send(SseEmitter.event()
                        .name(eventName)
                        .id(UUID.randomUUID().toString())
                        .data(data));
            } catch (IOException e) {
                removeEmitter(jobId, sid);
            }
        });
    }

    public void completeJob(String jobId) {
        Map<String, SseEmitter> subscribers = emittersByJob.get(jobId);
        if (subscribers == null || subscribers.isEmpty()) {
            return;
        }
        subscribers.forEach((subscriberId, emitter) -> {
            try {
                emitter.complete();
            } catch (Exception e) {

            }
        });
    }

    private void removeEmitter(String jobId, String subscriberId) {
        Map<String, SseEmitter> subscribers = emittersByJob.get(jobId);
        if (subscribers == null)
            return;

        subscribers.remove(subscriberId);

        if (subscribers.isEmpty()) {
            emittersByJob.remove(jobId);
        }
    }
}
