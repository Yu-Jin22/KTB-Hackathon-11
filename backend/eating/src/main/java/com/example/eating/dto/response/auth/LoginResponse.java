package com.example.eating.dto.response.auth;

import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class LoginResponse {
    private boolean isLoginSuccess;
    private String loginId;
}
