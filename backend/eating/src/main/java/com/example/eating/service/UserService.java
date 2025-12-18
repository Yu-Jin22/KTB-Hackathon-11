package com.example.eating.service;

import org.springframework.stereotype.Service;

import com.example.eating.domain.User;
import com.example.eating.dto.request.user.SignupDto;
import com.example.eating.dto.response.user.SignupResponse;
import com.example.eating.repository.UserRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;

    public SignupResponse signup(SignupDto dto) {
        try {
            User user = User.builder()
                    .email(dto.getEmail().trim())
                    .password(dto.getPassword().trim())
                    .nickname(dto.getNickname().trim())
                    .build();

            User saved = userRepository.save(user);
            return SignupResponse.builder()
                    .isSignupSuccess(true)
                    .email(saved.getEmail())
                    .nickname(saved.getNickname())
                    .build();
        } catch (Exception e) {
            return SignupResponse.builder()
                    .isSignupSuccess(false)
                    .build();
        }
    }

    public boolean existsById(Long userId) {
        if (userId == null) {
            throw new IllegalArgumentException("User ID cannot be null");
        }
        return userRepository.existsById(userId);
    }

    public User getUserById(Long userId) {
        if (userId == null) {
            throw new IllegalArgumentException("User ID cannot be null");
        }
        return userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("User not found with id: " + userId));
    }

    public void deleteUserById(Long userId) {
        if (userId == null) {
            throw new IllegalArgumentException("User ID cannot be null");
        }
        userRepository.deleteById(userId);
    }
}
