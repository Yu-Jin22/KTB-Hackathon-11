package com.example.eating.dto.response.s3;

import lombok.Builder;
import lombok.Getter;


@Getter
@Builder
public class PresignedUrlResponse {

    private String uploadUrl;

    private String fileUrl;
}