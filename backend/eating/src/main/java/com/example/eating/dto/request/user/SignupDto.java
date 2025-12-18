package com.example.eating.dto.request.user;

import lombok.Getter;

@Getter
public class SignupDto {
    private String email;
    private String password;
    private String nickname;
}
