package com.test.controller;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.stereotype.Controller;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;

import javax.servlet.http.HttpServletRequest;
import java.io.File;
import java.io.IOException;
import java.time.Duration;

@Controller
@RequestMapping("/llm")
public class LLMcall {

    private final WebClient webClient = WebClient.create();

    @Value("${chatURL}")
    private String chatUrl;
    @Value("${pdfURL}")
    private String pdfUrl;

    @PostMapping("/chat")
    @ResponseBody
    public Flux<ServerSentEvent<String>> proxyRequest(
            @RequestHeader HttpHeaders headers,
            @RequestBody String body
    ) {
        System.out.println("Chat URL: " + chatUrl);
        System.out.println("Request Body: " + body);

        // 使用 WebClient 发起请求，并将流式响应转为 SSE 格式
        return webClient.post() //发起post请求
                .uri(chatUrl)   //请求的地址
                .headers(httpHeaders -> httpHeaders.addAll(headers))  // 转发请求头
                .contentType(MediaType.APPLICATION_JSON)  // 设置内容类型为 JSON
                .bodyValue(body)  // 转发请求体
                .accept(MediaType.TEXT_EVENT_STREAM)  // 接受流式响应 (SSE)
                .retrieve() //获取 HTTP 响应。
                .bodyToFlux(String.class)  // 将响应体转为 Flux<String> 流
                .map(data -> ServerSentEvent.builder(data).build())  // 将每条数据封装成 SSE
                .delayElements(Duration.ofMillis(100));  // 模拟延迟，保证实时性体验
    }


    @PostMapping("/analysepdf")
    @ResponseBody
    public Flux<ServerSentEvent<String>> proxyPdfRequest(
            @RequestHeader HttpHeaders headers,
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "stream",required = false) String stream,
            @RequestParam(value = "db",required = false) String collection
    ) throws IOException {
        System.out.println("PDF URL: " + pdfUrl);
        System.out.println("File Name: " + file.getOriginalFilename());

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", new ByteArrayResource(file.getBytes()) {
            @Override
            public String getFilename() {
                return file.getOriginalFilename();
            }
        });
        body.add("stream",stream);
        body.add("db",collection);


        return webClient.post()
                .uri(pdfUrl)
                .headers(httpHeaders -> httpHeaders.addAll(headers))
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .bodyValue(body)
                .accept(MediaType.TEXT_EVENT_STREAM)
                .retrieve()
                .bodyToFlux(String.class)
                .map(data -> ServerSentEvent.builder(data).build())
                .delayElements(Duration.ofMillis(100));
    }


    @RequestMapping("/test")
    @ResponseBody
    public String test(){
        return "successful";
    }

/*请求阻塞的测试代码，一直解决不了！
    @PostMapping("/analysepdf")
    @ResponseBody
    public Flux<ServerSentEvent<String>> testPdfRequest(
            @RequestHeader HttpHeaders headers,
            @RequestParam("file") MultipartFile file
    ) throws IOException {
        System.out.println("PDF URL: " +"http://127.0.0.1:8882/llm/pdf");
        System.out.println("File Name: " + file.getOriginalFilename());

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", new ByteArrayResource(file.getBytes()) {
            @Override
            public String getFilename() {
                return file.getOriginalFilename();
            }
        });

        return webClient.post()
                .uri("http://127.0.0.1:8882/llm/pdf")
                .headers(httpHeaders -> httpHeaders.addAll(headers))
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .bodyValue(body)
                .accept(MediaType.TEXT_EVENT_STREAM)
                .retrieve()
                .bodyToFlux(String.class)
                .map(data -> ServerSentEvent.builder(data).build())
                .delayElements(Duration.ofMillis(100));
    }


    //FIXME:问题处在转发请求的请求体里面，如果加上@RequestBody String body就会阻塞
    @PostMapping("/pdf")
    public ResponseEntity<String> uploadPdf(@RequestParam("file") MultipartFile file,
                                            //@RequestBody String body,
                                            HttpServletRequest request) throws IOException {
        if (file.isEmpty()) {
            return ResponseEntity.status(400).body("文件为空，请选择一个PDF文件上传。");
        }

        // 打印文件信息
        System.out.println("文件名: " + file.getOriginalFilename());
        System.out.println("文件大小: " + file.getSize() + " bytes");
        System.out.println("文件类型: " + file.getContentType());

        // 打印请求头信息
        System.out.println("请求头信息:");
        request.getHeaderNames().asIterator().forEachRemaining(headerName -> {
            System.out.println(headerName + ": " + request.getHeader(headerName));
        });

        // 打印请求参数信息
        System.out.println("请求参数信息:");
        request.getParameterMap().forEach((key, value) -> {
            System.out.println(key + ": " + String.join(", ", value));
        });
        //System.out.println("Request Body: " + body);

        // 这里可以添加将文件保存到服务器的代码
        // 例如: file.transferTo(new File("path/to/destination/" + file.getOriginalFilename()));
        //获取工作区路径
        String projectPath = System.getProperty("user.dir");
        file.transferTo(new File(projectPath+"/proxyLLM/src/main/resources/pdf/" + file.getOriginalFilename()));

        return ResponseEntity.ok("PDF文件上传成功！");
    }*/
}

