package com.example.eating.service;

import org.springframework.stereotype.Service;

import com.example.eating.domain.User;
import com.example.eating.dto.request.auth.LoginDto;
import com.example.eating.dto.response.auth.LoginResponse;
import com.example.eating.repository.UserRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;

    public LoginResponse login(LoginDto dto) {
        String email = dto.getEmail().trim();
        String password = dto.getPassword().trim();

        User savedUser = userRepository.findByEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("User not found with email: " + email));

        if (!savedUser.getEmail().equals(email) || !savedUser.getPassword().equals(password)) {
            throw new IllegalArgumentException("Invalid login credentials");
        }

        // 로그인 성공 응답 반환
        return LoginResponse.builder()
                .isLoginSuccess(true)
                .email(email)
                .nickname(savedUser.getNickname())
                .build();
    }
}
