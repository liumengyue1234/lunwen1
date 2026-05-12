package com.pinewilt.detection.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.*;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@TableName("detection_task")
public class DetectionTask {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;
    private String taskName;
    private String imageName;
    private String imagePath;
    private String modelName;
    private Float confThreshold;
    private String status;        // PENDING / PROCESSING / DONE / FAILED
    private Integer detectCount;
    private String resultImage;
    private String resultJson;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    private LocalDateTime finishTime;
}
