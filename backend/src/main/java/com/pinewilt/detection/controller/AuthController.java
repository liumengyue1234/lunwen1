package com.pinewilt.detection.controller;

import com.pinewilt.detection.config.JwtUtil;
import com.pinewilt.detection.dto.ApiResponse;
import com.pinewilt.detection.dto.LoginRequest;
import com.pinewilt.detection.entity.User;
import com.pinewilt.detection.mapper.UserMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.*;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthenticationManager authManager;
    private final JwtUtil jwtUtil;
    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;

    @PostMapping("/login")
    public ApiResponse<Map<String, Object>> login(@RequestBody LoginRequest req) {
        try {
            authManager.authenticate(
                    new UsernamePasswordAuthenticationToken(req.getUsername(), req.getPassword()));
        } catch (AuthenticationException e) {
            return ApiResponse.fail(401, "用户名或密码错误");
        }
        User user = userMapper.selectOne(
                new LambdaQueryWrapper<User>().eq(User::getUsername, req.getUsername()));
        String token = jwtUtil.generateToken(req.getUsername());
        return ApiResponse.ok(Map.of(
                "token", token,
                "username", user.getUsername(),
                "realName", user.getRealName() != null ? user.getRealName() : user.getUsername(),
                "role", user.getRole()
        ));
    }

    @PostMapping("/register")
    public ApiResponse<String> register(@RequestBody LoginRequest req) {
        if (userMapper.selectOne(new LambdaQueryWrapper<User>()
                .eq(User::getUsername, req.getUsername())) != null) {
            return ApiResponse.fail(400, "用户名已存在");
        }
        User user = new User();
        user.setUsername(req.getUsername());
        user.setPassword(passwordEncoder.encode(req.getPassword()));
        user.setRole("USER");
        user.setStatus(1);
        userMapper.insert(user);
        return ApiResponse.ok("注册成功");
    }
}
