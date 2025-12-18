package com.example.eating.dto.response.user;

import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class SignupResponse {
    private boolean isSignupSuccess;
    private String email;
    private String nickname;
}
