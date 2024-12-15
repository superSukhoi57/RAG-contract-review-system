
import React, { useState } from 'react';

const baichuan = process.env.REACT_APP_CNTREVIEW;

//定义一个父组件
const Baichuan3: React.FC = () => {
    const [uploadResponse, setUploadResponse] = useState(null);

    const handleUploadResponse = (response: any) => {
        setUploadResponse(response);
    };


    return (
        <div>
            <BaichuanUpload3 setfunction={handleUploadResponse} />
            <OtherComponent valueofresponse={uploadResponse} />
        </div>
    )

}
export default Baichuan3;

//定义一个接口
interface BaichuanPorps {
    //这个接口的属性是一个函数，函数的参数是any类型，返回值是void
    setfunction: (response: any) => void;
}
interface OtherComponentProps {
    valueofresponse: any;
}

//定义一个子组件
const BaichuanUpload3: React.FC<BaichuanPorps> = ({ setfunction }) => {
    const [isFileSelected, setIsFileSelected] = useState(false);
    /*
    <File | null>:
这是 TypeScript 的类型注解，指定状态变量的类型。
File 表示状态可以是一个文件对象。
null 表示状态也可以是 null，即没有文件被选中时的初始状态。
(null):
这是 useState 的初始值。
在组件首次渲染时，状态变量的初始值为 null。
    */
    const [pdf, setPdf] = useState<File | null>(null);
    // 处理文件选择
    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            setPdf(file);
            setIsFileSelected(true);
        } else {
            setIsFileSelected(false);
        }
    };

    //开始审查
    function cntreview() {

        const formData = new FormData();
        if (pdf) {
            formData.append('file', pdf);
        }
        //打印pdf名字
        console.log('pdf:', pdf);

        console.log('formData:', formData);
        fetch(baichuan, {
            method: 'POST',
            headers: {
                /*
                在使用 FormData 对象时，不需要手动设置 Content-Type 头。浏览器会自动为你设置正确的
                Content-Type，包括必要的边界信息。如果你手动设置 Content-Type 为 application/form-data，
                会导致缺少边界信息，从而导致服务器无法正确解析请求，返回 400 错误。
                */
                //'Content-Type': 'application/form-data',
                'Accept': 'text/event-stream',//接受流式响应
            },
            body: formData,
        })
            .then((response) => {
                const reader = response.body.getReader();
                const decoder = new TextDecoder('utf-8');
                setfunction('');//清空之前的对话

                const readStream = () => {
                    reader.read().then(({ done, value }) => {
                        if (done) {
                            console.log('Stream complete');
                            return;
                        }
                        const chunk = decoder.decode(value, { stream: true });
                        let word;
                        console.log('Received chunk:', chunk);
                        const regex = /{"content":".{0,32}"}/
                        word = chunk.match(regex);
                        console.log('wordtype:', typeof word);

                        try {
                            //将word转换为字符串
                            word = word.toString();
                            console.log('wordtype:', typeof word);
                            console.log('%s regex: %s', regex.test(chunk), word);
                            word = JSON.parse(word);
                            word = word.content;
                            console.log('word:', word);
                        } catch (e) {
                            console.log('e:', e);
                            word = "";
                        }
                        // Process the chunk here (e.g., update state or UI)
                        setfunction((prevData) => prevData + word);
                        // Continue reading the stream
                        readStream();
                    }).catch((error) => {
                        console.error('Stream reading error:', error);
                    });
                };

                // Start reading the stream
                readStream();
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    return (
        <div>
            <h1>Upload PDF:</h1>
            <input type="file" id="file" name="file" onChange={handleFileChange} />
            <button onClick={cntreview} disabled={!isFileSelected}>开始审查</button>
        </div>
    )
}

const OtherComponent: React.FC<OtherComponentProps> = ({ valueofresponse }) => {

    return (
        <span>
            {valueofresponse}
        </span>
    );
}