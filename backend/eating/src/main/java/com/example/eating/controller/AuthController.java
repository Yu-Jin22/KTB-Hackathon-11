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

@Controller
@RequestMapping("auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    // 더미 유저 로그인 처리
    // "loginId": "test", "loginPassword": "test"
    @PostMapping("/login")
    public ResponseEntity<LoginResponse> login(@RequestBody LoginDto dto) {
        LoginResponse response = authService.login(dto);
        return ResponseEntity.ok().body(response);
    }
}
