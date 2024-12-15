package com.test.controller;
import com.spire.pdf.PdfDocument;
import com.spire.pdf.comparison.PdfComparer;
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Stream;


/*
这段pdf对比的逻辑是前端上传pdf一次上传一个，后端创建一个文件夹存放pdf，而且文件夹的容量是2。
当超过2时有一个delete2函数来处理，保证数量一直是2。当前端点击开始对比时，/pdf的方法会获取文件夹
里面的两个pdf然后开始对比，将对比的结果存在一个文件夹，然后返回，此时结果不会被删除，当用户多次点击时候可以返回
用户对比返回结果的同时会删除之前的待对比文件
 */

@Controller
@CrossOrigin
public class FilesUpload {

    //获取工作区路径
    public String projectPath = System.getProperty("user.dir");

    @PostMapping("/upload")
    @ResponseBody
    public String upload(@RequestParam("file")MultipartFile myFile) throws IOException {//这个参数名字和表单提交的名字要相同
        //把文件内容存到本地磁盘上：
        String originalName=myFile.getOriginalFilename();
        //解决同名文件覆盖：
        //int dotIndex=originalName.lastIndexOf(".");//就是扩展名的那个点
        //originalName= UUID.randomUUID().toString()+originalName;


        String filePath=projectPath+"/pdfCompare/src/main/resources/repository/raw/"+originalName;

        //正确的:
        //myFile.transferTo(new File("D:\\the_files_at\\Assignment\\Project\\contractReview\\project\\backStage\\pdfCompare\\src\\main\\resources\\repository\\raw\\"+originalName));
        myFile.transferTo(new File(filePath));

        //相对路径从C盘的tomcat。。下开始 C:\Users\86158\AppData\Local\Temp\tomcat.8080.61982617445817683\work\Tomcat\localhost\ROOT\.\src\main\java\resources\repository\get(1).html
        //myFile.transferTo(new File("./src/main/java/resources/repository/"+originalName));

        //确保文件夹里面同一时间只有两个文件
        deletegt2();

        return  "文件上传成功，URL：....";
    }


    @GetMapping("/pdf")
    @ResponseBody
    public ResponseEntity<InputStreamResource> returnPdf() throws IOException {
        //遍历要对比的文件夹下的文件
        String directoryPath = projectPath+"/pdfCompare/src/main/resources/repository/raw/";
        String resultpath=projectPath+"/pdfCompare/src/main/resources/repository/processed/result.pdf";
        List<String> filePaths = new ArrayList<>();
        try (Stream<Path> paths = Files.list(Paths.get(directoryPath))) {
            paths
                    .filter(Files::isRegularFile) // 过滤出所有的文件，不包括目录
                    .forEach(path -> {//将文件的绝对路径加入到数组
                        filePaths.add(path.toString());
                    });
        } catch (Exception e) {
            e.printStackTrace();
        }
        PdfComparer comparer = null;



            if (filePaths.size() ==2) {

            //将数组里的文件拿出来比较
            //创建一个PdfDocument类对象并加载一个PDF文档
            PdfDocument pdf1 = new PdfDocument();
            pdf1.loadFromFile(filePaths.get(0));

            //创建另一个PdfDocument类对象并加载另一个PDF文档
            PdfDocument pdf2 = new PdfDocument();
            pdf2.loadFromFile(filePaths.get(1));

            //创建一个PdfComparer类的对象
            comparer = new PdfComparer(pdf1, pdf2);

                //比较两个PDF 档并将比较结果保存到一个新文档中
                comparer.compare(resultpath);
        }

        //准备返回！D:\the_files_at\Assignment\Project\contractReview\project\backStage\pdfCompare\src\main\resources\repository\processed
        File file = new File(resultpath);
        HttpHeaders headers = new HttpHeaders();
        headers.add("Content-Disposition", "inline; filename=result.pdf");

        //对比完，用完就删掉raw里所有的文件。因为每次在process的都是同名的会被覆盖所以不用删
        try {
            try (Stream<Path> paths = Files.list(Paths.get(directoryPath))) {
                paths
                        .filter(Files::isRegularFile) // 过滤出所有的文件，不包括目录
                        .forEach(path -> { // 对每个文件执行操作
                            try {
                                Files.delete(path); // 删除文件
                            } catch (IOException e) {
                                e.printStackTrace();
                            }
                        });
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        return ResponseEntity
                .ok()
                .headers(headers)
                .contentType(MediaType.APPLICATION_PDF)
                .body(new InputStreamResource(new FileInputStream(file)));
    }
/*

response.setHeader("Content-Disposition", "inline; filename=\"" + pdfFile.getName() + "\"");
当`Content-Disposition`的值是`inline`时，大多数现代浏览器会尝试在浏览器内打开PDF文件，而不是下载它。如果你想要浏览器下载文件而不是在浏览器内打开，你应该将`inline`改为`attachment`：
response.setHeader("Content-Disposition", "attachment; filename=\"" + pdfFile.getName() + "\"");
使用`attachment`值，浏览器通常会弹出一个保存文件的对话框，提示用户保存文件到本地。
以下是两种情况的浏览器行为：
- **inline**: 浏览器尝试在新的标签页或窗口中显示PDF文件，如果浏览器不支持PDF的内置查看，它可能会提示用户下载。
- **attachment**: 浏览器总是提示用户下载文件。
请根据你的需求选择合适的`Content-Disposition`值。
 */


    //处理指定文件夹下文件数量大3的文件
    public  void deletegt2() {
        String directoryPath = projectPath+"/pdfCompare/src/main/resources/repository/raw/"; // 你的文件夹路径
        try {
            Path dirPath = Paths.get(directoryPath);
            try (Stream<Path> files = Files.list(dirPath)) {
                long count = files.count();
                if (count > 2) {
                    deleteOldestFile(dirPath);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }


    /*
    Files.list(dirPath): 这行代码使用java.nio.file.Files类的list(Path dir)方法列出给定目录下的所有文件和目录。这个方法返回一个Stream<Path>对象，每个Path对象代表目录中的一个文件或目录。
.filter(Files::isRegularFile): 这行代码使用filter方法和Files类的isRegularFile(Path path)方法过滤出所有的普通文件（不包括目录和其他非文件类型的路径）。
.min(Comparator.comparingLong(p -> {...})): 这行代码找出最早创建的文件。它使用min方法和一个比较器，比较器通过Files.getLastModifiedTime(Path path)方法获取每个文件的最后修改时间，并将其转换为毫秒值。最后修改时间在这里用作文件的创建时间。
.ifPresent(p -> {...}): 如果找到了最早创建的文件（即min方法返回的Optional对象包含一个值），那么这行代码就会执行一个操作，删除这个文件。这个操作通过Files.delete(Path path)方法实现。
总的来说，这段代码的作用是删除给定目录中最早创建的文件
     */
    private  void deleteOldestFile(Path dirPath) throws IOException {
        Files.list(dirPath)
                .filter(Files::isRegularFile)
                .min(Comparator.comparingLong(p -> {
                    try {
                        return Files.getLastModifiedTime(p).toMillis();
                    } catch (IOException e) {
                        throw new RuntimeException(e);
                    }
                }))
                .ifPresent(p -> {
                    try {
                        Files.delete(p);
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                });
    }


}
