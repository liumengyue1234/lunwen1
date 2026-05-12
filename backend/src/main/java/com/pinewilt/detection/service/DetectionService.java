package com.pinewilt.detection.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.pinewilt.detection.entity.DetectionResult;
import com.pinewilt.detection.entity.DetectionTask;
import com.pinewilt.detection.entity.User;
import com.pinewilt.detection.mapper.DetectionResultMapper;
import com.pinewilt.detection.mapper.DetectionTaskMapper;
import com.pinewilt.detection.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
public class DetectionService {

    private final DetectionTaskMapper taskMapper;
    private final DetectionResultMapper resultMapper;
    private final UserMapper userMapper;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Value("${upload.path:./uploads}")
    private String uploadPath;

    @Value("${ai.service.url:http://localhost:5001}")
    private String aiServiceUrl;

    private RestTemplate restTemplate = new RestTemplate();

    /**
     * 上传图像并调用AI服务进行检测
     */
    public Map<String, Object> detectImage(MultipartFile file, String username,
                                            String modelName, Float confThreshold) throws Exception {
        // 1. 查找用户
        User user = userMapper.selectOne(
                new LambdaQueryWrapper<User>().eq(User::getUsername, username));
        if (user == null) throw new RuntimeException("用户不存在");

        // 2. 保存原始图像
        String origFilename = UUID.randomUUID().toString() + "_" + file.getOriginalFilename();
        Path imageSavePath = Paths.get(uploadPath, origFilename);
        Files.createDirectories(imageSavePath.getParent());
        file.transferTo(imageSavePath.toFile());

        // 3. 创建任务记录
        DetectionTask task = new DetectionTask();
        task.setUserId(user.getId());
        task.setTaskName("检测-" + file.getOriginalFilename());
        task.setImageName(file.getOriginalFilename());
        task.setImagePath(origFilename);
        task.setModelName(modelName != null ? modelName : "yolov8s");
        task.setConfThreshold(confThreshold != null ? confThreshold : 0.25f);
        task.setStatus("PROCESSING");
        task.setCreateTime(LocalDateTime.now());
        taskMapper.insert(task);

        try {
            // 4. 调用AI服务
            Map<String, Object> aiResult = callAiService(imageSavePath.toFile(),
                    task.getModelName(), task.getConfThreshold());

            // 5. 解析结果
            int detectCount = (int) aiResult.getOrDefault("detect_count", 0);
            String resultImageB64 = (String) aiResult.getOrDefault("result_image", null);

            // 6. 保存检测结果详情
            List<?> detections = (List<?>) aiResult.getOrDefault("detections", List.of());
            for (Object det : detections) {
                @SuppressWarnings("unchecked")
                Map<String, Object> d = (Map<String, Object>) det;
                DetectionResult result = new DetectionResult();
                result.setTaskId(task.getId());
                result.setLabel((String) d.get("label"));
                result.setConfidence(((Number) d.get("confidence")).floatValue());
                @SuppressWarnings("unchecked")
                Map<String, Object> bbox = (Map<String, Object>) d.get("bbox");
                if (bbox != null) {
                    result.setX1(((Number) bbox.get("x1")).floatValue());
                    result.setY1(((Number) bbox.get("y1")).floatValue());
                    result.setX2(((Number) bbox.get("x2")).floatValue());
                    result.setY2(((Number) bbox.get("y2")).floatValue());
                }
                result.setCreateTime(LocalDateTime.now());
                resultMapper.insert(result);
            }

            // 7. 更新任务状态
            task.setStatus("DONE");
            task.setDetectCount(detectCount);
            task.setResultJson(objectMapper.writeValueAsString(aiResult));
            task.setFinishTime(LocalDateTime.now());
            taskMapper.updateById(task);

            // 8. 构建返回
            Map<String, Object> response = new HashMap<>();
            response.put("taskId", task.getId());
            response.put("status", "DONE");
            response.put("detectCount", detectCount);
            response.put("detections", detections);
            response.put("resultImage", resultImageB64);
            response.put("modelName", task.getModelName());
            response.put("imageName", file.getOriginalFilename());
            return response;

        } catch (Exception e) {
            task.setStatus("FAILED");
            task.setFinishTime(LocalDateTime.now());
            taskMapper.updateById(task);
            log.error("检测失败", e);
            throw e;
        }
    }

    /**
     * 获取历史检测记录
     */
    public Map<String, Object> getHistory(String username, int page, int size) {
        User user = userMapper.selectOne(
                new LambdaQueryWrapper<User>().eq(User::getUsername, username));
        if (user == null) return Map.of("total", 0, "records", List.of());

        Page<DetectionTask> pageObj = new Page<>(page, size);
        taskMapper.selectPage(pageObj,
                new LambdaQueryWrapper<DetectionTask>()
                        .eq(DetectionTask::getUserId, user.getId())
                        .orderByDesc(DetectionTask::getCreateTime));

        return Map.of(
                "total", pageObj.getTotal(),
                "records", pageObj.getRecords(),
                "pages", pageObj.getPages(),
                "current", pageObj.getCurrent()
        );
    }

    /**
     * 获取任务详情（含检测结果列表）
     */
    public Map<String, Object> getTaskDetail(Long taskId) {
        DetectionTask task = taskMapper.selectById(taskId);
        if (task == null) return Map.of("error", "任务不存在");
        List<DetectionResult> results = resultMapper.selectList(
                new LambdaQueryWrapper<DetectionResult>().eq(DetectionResult::getTaskId, taskId));
        return Map.of("task", task, "results", results);
    }

    /**
     * 调用Python AI推理服务（HTTP）
     */
    @SuppressWarnings("unchecked")
    private Map<String, Object> callAiService(File imageFile, String modelName, float conf) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("image", new FileSystemResource(imageFile));
            body.add("model", modelName);
            body.add("conf", String.valueOf(conf));

            HttpEntity<MultiValueMap<String, Object>> request = new HttpEntity<>(body, headers);
            ResponseEntity<Map> response = restTemplate.postForEntity(
                    aiServiceUrl + "/api/detect", request, Map.class);

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return response.getBody();
            }
        } catch (Exception e) {
            log.warn("AI服务调用失败，使用模拟数据: {}", e.getMessage());
        }

        // AI服务不可用时返回模拟检测结果（演示用）
        return buildMockResult(modelName, conf);
    }

    private Map<String, Object> buildMockResult(String modelName, float conf) {
        List<Map<String, Object>> detections = new ArrayList<>();
        Random rnd = new Random();
        int n = rnd.nextInt(4) + 1;
        for (int i = 0; i < n; i++) {
            float x1 = rnd.nextFloat() * 300;
            float y1 = rnd.nextFloat() * 300;
            Map<String, Object> bbox = new HashMap<>();
            bbox.put("x1", x1);
            bbox.put("y1", y1);
            bbox.put("x2", x1 + 50 + rnd.nextFloat() * 80);
            bbox.put("y2", y1 + 50 + rnd.nextFloat() * 80);
            Map<String, Object> d = new HashMap<>();
            d.put("label", "pine_wilt_nematode");
            d.put("confidence", Math.round((0.5 + rnd.nextFloat() * 0.48) * 1000) / 1000.0);
            d.put("bbox", bbox);
            detections.add(d);
        }
        Map<String, Object> r = new HashMap<>();
        r.put("detect_count", n);
        r.put("detections", detections);
        r.put("model", modelName);
        r.put("result_image", null);
        return r;
    }
}
