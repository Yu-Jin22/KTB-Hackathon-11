package com.example.eating.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class WebClientConfig {

    @Bean
    public WebClient fastApiClient() {
        return WebClient.builder()
                .baseUrl("http://localhost:8000") // FastAPI 주소
                .build();
    }
}