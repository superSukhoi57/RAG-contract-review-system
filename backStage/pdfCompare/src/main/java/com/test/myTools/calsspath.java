package com.test.myTools;

public class calsspath {
    public static void main(String[] args) {
        // TODO:获取当前类的路径
        String projectPath = System.getProperty("user.dir");
        System.out.println("Project Path: " + projectPath);
    }
}
