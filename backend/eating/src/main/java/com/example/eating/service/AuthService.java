package com.example.eating.service;

import org.springframework.stereotype.Service;

import com.example.eating.domain.User;
import com.example.eating.dto.request.auth.LoginDto;
import com.example.eating.dto.response.auth.LoginResponse;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class AuthService {

    // 더미 유저 로그인 처리
    // "loginId": "test", "loginPassword": "test"
    private final User dummyUser = new User("test", "test");

    public LoginResponse login(LoginDto dto) {
        String reqLoginId = dto.getLoginId();
        String reqLoginPassword = dto.getLoginPassword();

        // 더미 유저와 입력된 로그인 정보 비교
        if (!dummyUser.getLoginId().equals(reqLoginId) || !dummyUser.getLoginPassword().equals(reqLoginPassword)) {
            throw new IllegalArgumentException("Invalid login credentials");
        }

        // 로그인 성공 응답 반환
        return LoginResponse.builder()
                .isLoginSuccess(true)
                .loginId(reqLoginId)
                .build();
    }
}
