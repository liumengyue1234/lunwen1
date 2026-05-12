package com.pinewilt.detection.controller;

import com.pinewilt.detection.dto.ApiResponse;
import com.pinewilt.detection.service.DetectionService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/detection")
@RequiredArgsConstructor
public class DetectionController {

    private final DetectionService detectionService;

    /**
     * POST /api/detection/detect
     * 上传CT图像进行检测
     */
    @PostMapping("/detect")
    public ApiResponse<Map<String, Object>> detect(
            @RequestParam("image") MultipartFile file,
            @RequestParam(value = "model", defaultValue = "yolov8s") String modelName,
            @RequestParam(value = "conf", defaultValue = "0.25") Float conf,
            Authentication auth) {
        try {
            Map<String, Object> result = detectionService.detectImage(
                    file, auth.getName(), modelName, conf);
            return ApiResponse.ok(result);
        } catch (Exception e) {
            return ApiResponse.fail("检测失败: " + e.getMessage());
        }
    }

    /**
     * GET /api/detection/history?page=1&size=10
     */
    @GetMapping("/history")
    public ApiResponse<Map<String, Object>> history(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size,
            Authentication auth) {
        Map<String, Object> result = detectionService.getHistory(auth.getName(), page, size);
        return ApiResponse.ok(result);
    }

    /**
     * GET /api/detection/task/{id}
     */
    @GetMapping("/task/{id}")
    public ApiResponse<Map<String, Object>> taskDetail(@PathVariable Long id) {
        return ApiResponse.ok(detectionService.getTaskDetail(id));
    }

    /**
     * GET /api/detection/models — 获取可用模型列表
     */
    @GetMapping("/models")
    public ApiResponse<List<Map<String, String>>> models() {
        return ApiResponse.ok(List.of(
                Map.of("value", "yolov8n", "label", "YOLOv8n (超轻量)"),
                Map.of("value", "yolov8s", "label", "YOLOv8s (标准)"),
                Map.of("value", "yolov5s", "label", "YOLOv5s"),
                Map.of("value", "yolov5m", "label", "YOLOv5m"),
                Map.of("value", "yolov9t", "label", "YOLOv9t"),
                Map.of("value", "yolov10n", "label", "YOLOv10n")
        ));
    }
}
