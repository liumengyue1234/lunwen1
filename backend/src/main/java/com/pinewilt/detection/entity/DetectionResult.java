package com.pinewilt.detection.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.*;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@TableName("detection_result")
public class DetectionResult {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long taskId;
    private String label;
    private Float confidence;
    private Float x1;
    private Float y1;
    private Float x2;
    private Float y2;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
