package com.example.eating.controller;

import com.example.eating.dto.request.s3.PresignedUrlRequest;
import com.example.eating.dto.response.s3.PresignedUrlResponse;
import com.example.eating.service.PresignedUrlService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/presigned-url")
@RequiredArgsConstructor
public class PresignedUrlController {

    private final PresignedUrlService presignedUrlService;

    @PostMapping
    public ResponseEntity<PresignedUrlResponse> generatePresignedUrl(@RequestBody PresignedUrlRequest dto) {
        log.info("event=fileName_received Method=POST path=/presigned-url fileName={}", dto.getFileName());

        PresignedUrlResponse response = presignedUrlService.createPresignedUrl(dto);

        log.info("event=generatePresignedUrl Method=POST path=/presigned-url uploadUrl={} fileUrl={}",
                response.getUploadUrl(), response.getFileUrl());
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

}
