
import React, { useState } from 'react';
import Selector from './collection_selector.tsx';

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

//这是一个子组件，展示大模型的响应
const OtherComponent: React.FC<OtherComponentProps> = ({ valueofresponse }) => {

    return (
        <span>
            {valueofresponse}
        </span>
    );
}
//定义另一个子组件，是上传文件并得到响应的组件
const BaichuanUpload3: React.FC<BaichuanPorps> = ({ setfunction }) => {

    //记录下拉列表选中的collection
    const [collection, setCollection] = useState('');
    //记录是否是流式响应，用单选框来选择
    const [isStream, setIsStream] = useState(false);
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
    // 在input组件里获取文件并处理文件，将文件存储到pdf状态变量中
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

        //加入collection
        formData.append('db', collection);


        //console.log('formData:', formData);


        if (!isStream) {
            formData.append('stream', 'False');//python的False不是false!因为是字符串还要转换，所以约定带参数不流式响应，不带默认流式
            setfunction('');//清空之前的对话
            //不是流式响应
            fetch(baichuan, {
                method: 'POST',
                body: formData,
            })
                .then(response => response.json())
                .then(data => {
                    console.log('data:', data)
                    setfunction(data.choices[0].message.content);
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            //直接返回，不执行下面的代码
            return;
        }

        console.log('使用流式响应');

        fetch(baichuan, {
            method: 'POST',
            headers: {

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
                        //console.log('Received chunk:', chunk);
                        const regex = /{"content":".{0,32}"}/
                        word = chunk.match(regex);
                        //console.log('wordtype:', typeof word);

                        try {
                            //将word转换为字符串
                            word = word.toString();
                            //console.log('wordtype:', typeof word);
                            //console.log('%s regex: %s', regex.test(chunk), word);
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
            请选择你的知识库：  <Selector notify={setCollection} />
            是否是流式响应：<input type="checkbox" onChange={() => setIsStream(!isStream)} />
            <h1>Upload PDF:</h1>
            <input type="file" id="file" name="file" onChange={handleFileChange} />
            <button onClick={cntreview} disabled={!isFileSelected}>开始审查</button>
        </div>
    )
}

