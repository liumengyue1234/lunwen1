package com.pinewilt.detection.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.pinewilt.detection.entity.User;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserMapper extends BaseMapper<User> {}
