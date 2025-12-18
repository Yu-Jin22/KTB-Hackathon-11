package com.example.eating.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;

import com.example.eating.dto.request.auth.LoginDto;
import com.example.eating.dto.response.auth.LoginResponse;
import com.example.eating.service.AuthService;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Controller
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/login")
    public ResponseEntity<LoginResponse> login(@RequestBody LoginDto dto) {
        log.info("event=http_in method=POST path=/api/auth/login email={}", dto.getEmail());

        LoginResponse response = authService.login(dto);

        log.info("event=login_success method=POST path=/api/auth/login login_success={}", response.isLoginSuccess());
        return ResponseEntity.ok().body(response);
    }
}
