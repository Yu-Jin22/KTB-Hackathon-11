package com.example.eating.controller;

import com.example.eating.dto.request.s3.PresignedUrlRequest;
import com.example.eating.dto.response.s3.PresignedUrlResponse;
import com.example.eating.service.PresignedUrlService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/presigned-url")
@RequiredArgsConstructor
public class PresignedUrlController {

    private final PresignedUrlService presignedUrlService;

    @PostMapping
    public ResponseEntity<PresignedUrlResponse> generatePresignedUrl(@RequestBody PresignedUrlRequest dto) {
        PresignedUrlResponse response = presignedUrlService.createPresignedUrl(dto);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

}
