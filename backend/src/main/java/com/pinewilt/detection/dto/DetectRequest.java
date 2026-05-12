package com.pinewilt.detection.dto;

import lombok.Data;
import java.util.List;

@Data
public class DetectRequest {
    private String modelName;
    private Float confThreshold;
}

// ─── Result DTOs ──────────────────────────────────────────────────────────────

@Data
class BboxDto {
    public float x1, y1, x2, y2;
}

@Data
class DetectionItemDto {
    public String label;
    public float confidence;
    public BboxDto bbox;
}

@Data
class AiServiceResponse {
    public String id;
    public String model;
    public String imageName;
    public int detectCount;
    public List<DetectionItemDto> detections;
    public String resultImage;   // base64
    public float confidenceThreshold;
    public String timestamp;
}
