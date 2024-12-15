import React, { useState } from 'react';
import { Input } from 'antd';

const baichuanchat = process.env.REACT_APP_BAICHUANCHAT;
console.log('baichuanchat:', baichuanchat);
const StreamChat: React.FC = () => {
    const [streamData, setStreamData] = useState('');
    //写一个文本输入框
    const [inputValue, setInputValue] = useState('');
    const handleInputChange = (e: any) => {
        setInputValue(e.target.value);
    };

    //点击发送按钮，将文本框的内容发送到百川
    const handleClick = () => {

        fetch(baichuanchat, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream',//接受流式响应
            },
            body: JSON.stringify({
                question: inputValue,
            }),
        })
            .then((response) => {
                const reader = response.body.getReader();
                const decoder = new TextDecoder('utf-8');
                setStreamData('');//清空之前的对话

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
                        setStreamData((prevData) => prevData + word);
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
    };

    //回车发送
    const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter') {
            handleClick();
        }
    };

    return (
        <div>
            <h1>百川对话组件</h1>
            <div>
                <h2>流式响应:</h2>
                <p>{streamData}</p>
            </div>
            <p>这是一个对话组件，可以和用户进行简单的对话。</p>
            <Input value={inputValue} onChange={handleInputChange} onKeyDown={handleKeyDown} />
            <button onClick={handleClick}>发送</button>
        </div>
    );
};

export default StreamChat;