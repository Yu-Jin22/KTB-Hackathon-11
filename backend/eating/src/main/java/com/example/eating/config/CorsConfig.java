package com.example.eating.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class CorsConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {

        registry.addMapping("/**")
                .allowedOriginPatterns("*") // ⭐ 모든 Origin 허용
                .allowedMethods("*")        // GET, POST, PUT, DELETE, OPTIONS 전부
                .allowedHeaders("*")        // 모든 헤더 허용 (X-USER-KEY 포함)
                .exposedHeaders("*")
                .allowCredentials(false)    // 쿠키/세션 안 쓰는 구조
                .maxAge(3600);
    }
}