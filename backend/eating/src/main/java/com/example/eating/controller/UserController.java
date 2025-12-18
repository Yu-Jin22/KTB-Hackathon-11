package com.example.eating.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;

import com.example.eating.dto.request.user.SignupDto;
import com.example.eating.dto.response.user.SignupResponse;
import com.example.eating.service.UserService;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Controller
@RequestMapping("/user")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @PostMapping("/signup")
    public ResponseEntity<SignupResponse> signup(@RequestBody SignupDto dto) {
        log.info("event=signup Method=POST path=/user/signup email={}", dto.getEmail());
        SignupResponse response = userService.signup(dto);
        return ResponseEntity.ok(response);
    }
}
