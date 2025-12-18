package com.example.eating.dto.request.s3;

import lombok.Getter;
import lombok.NoArgsConstructor;

/**
 * FastAPI → BE
 * S3 presigned-url 발급 요청
 */
@Getter
@NoArgsConstructor
public class PresignedUrlRequest {

    private String fileName;
    private String contentType;

    public PresignedUrlRequest(String fileName, String contentType) {
        this.fileName = fileName;
        this.contentType = contentType;
    }
}