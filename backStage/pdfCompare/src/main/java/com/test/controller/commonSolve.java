package com.test.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;


@Controller
@CrossOrigin
public class commonSolve {

    @GetMapping("/test")
    @ResponseBody
    public String uploadpdf(){
        //获取工作区路径
        String projectPath = System.getProperty("user.dir");
        System.out.println(projectPath);
        return "你好，已经成功连接了！！😘";

    }
}
