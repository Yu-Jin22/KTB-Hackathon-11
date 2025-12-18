package com.example.eating.dto.request.auth;

import lombok.Getter;

@Getter
public class LoginDto {
    private String email;
    private String password;
}