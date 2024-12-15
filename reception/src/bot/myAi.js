
//导入样式
import './myoutline.css';
const Myai = () => {

    const botId = "7393601461374566419";
    const personalAccessToken = "pat_6Zh96Icz5YRHOpDIUylPn2ZUdwEX2JMss7GaKSf6f4Jiswjgnf5XOTKSvAPDNd0p";
    let conversationId = null;

    async function createConversation() {
        const url = 'https://api.coze.cn/v1/conversation/create';
        const data = {};

        return fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${personalAccessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                console.log('创建会话响应:', data);
                // document.getElementById('response-container').innerText += JSON.stringify(data, null, 2) + '\n\n'; // 输出完整的响应内容
                if (data.code !== 0) {
                    throw new Error('创建会话失败');
                }
                if (!data.data || !data.data.id) {
                    throw new Error('响应数据中缺少会话ID');
                }
                conversationId = data.data.id;
                return conversationId;
            })
            .catch(error => {
                console.error('创建会话时出错:', error);
                document.getElementById('error-container').innerText = '创建会话时出错: ' + error.message;
                throw error;
            });
    }

    async function checkConversationStatus(chatId) {
        const url = `https://api.coze.cn/v3/chat/retrieve?chat_id=${chatId}&conversation_id=${conversationId}`;
        return fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${personalAccessToken}`,
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                console.log('查看对话详情响应:', data);
                // document.getElementById('response-container').innerText += JSON.stringify(data, null, 2) + '\n\n'; // 输出完整的响应内容
                if (data.code !== 0) {
                    throw new Error('查看对话详情失败');
                }
                return data.data.status;
            })
            .catch(error => {
                console.error('查看对话详情时出错:', error);
                document.getElementById('error-container').innerText = '查看对话详情时出错: ' + error.message;
                throw error;
            });
    }

    async function pollConversationStatus(chatId) {
        let status = await checkConversationStatus(chatId);
        while (status !== 'completed' && status !== 'required_action') {
            await new Promise(resolve => setTimeout(resolve, 2000)); // 等待2秒
            status = await checkConversationStatus(chatId);
        }
        return status;
    }

    async function sendMessage() {
        const userInput = document.getElementById('user-input');
        const chatMessages = document.getElementById('chat-messages');
        const responseContainer = document.getElementById('response-container');
        const errorContainer = document.getElementById('error-container');
        let myquestion;
        if (userInput.value.trim() !== "") {
            const userMessage = document.createElement('div');
            userMessage.textContent = "你：" + userInput.value;
            chatMessages.appendChild(userMessage);

            // let prompt = " ; 备注“下面json的key：ID表示货物的id，Message是对物体的描述，Location表示物体的具体位置，In Time表示物体的入库时间，Out Time表示物体的出库时间”。";
            //异步函数，忘记等他执行完了再执行下面的代码，导致传给api的数据是上一次的数据，导致回答不可预测
            /*    await fetch('http://localhost:8881/common/allmsg')
                   .then(res => res.json()).then(data => {
                       myquestion = userInput.value// + prompt + JSON.stringify(data.data);
                       userInput.value = "";
                   }) */

            myquestion = userInput.value// + prompt + JSON.stringify(data.data);
            userInput.value = "";
            //console.log(myquestion);
            try {
                if (!conversationId) {
                    await createConversation();
                }

                const url = `https://api.coze.cn/v3/chat?conversation_id=${conversationId}`;
                const data = {
                    bot_id: botId,
                    user_id: "123456789",
                    stream: false,
                    auto_save_history: true,
                    additional_messages: [
                        {
                            role: "user",
                            content: myquestion,
                            content_type: "text"
                        }
                    ]
                };

                //
                myquestion = "";
                const chatData = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${personalAccessToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                })
                    .then(response => response.json())
                    .then(data => {
                        console.log('发送消息响应:', data);
                        // responseContainer.innerText += JSON.stringify(data, null, 2) + '\n\n'; // 输出完整的响应内容
                        if (data.code !== 0) {
                            throw new Error('发送消息失败');
                        }
                        if (!data.data || !data.data.id) {
                            throw new Error('响应数据中缺少消息ID');
                        }
                        return data;
                    });

                await pollConversationStatus(chatData.data.id);

                const messageUrl = `https://api.coze.cn/v3/chat/message/list?chat_id=${chatData.data.id}&conversation_id=${conversationId}`;
                const messageData = await fetch(messageUrl, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${personalAccessToken}`,
                        'Content-Type': 'application/json'
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        console.log('获取消息详情响应:', data);
                        // responseContainer.innerText += JSON.stringify(data, null, 2) + '\n\n'; // 输出完整的响应内容
                        if (data.code !== 0) {
                            throw new Error('获取消息详情失败');
                        }
                        return data;
                    });



                // 忽略第一次返回的content内容
                const botMessages = messageData.data.slice(1).map(message => message.content).join('\n');
                const botMessage = document.createElement('div');
                botMessage.style.border = "1px solid #ccc";
                botMessage.style.borderRadius = "5px";
                botMessage.style.backgroundColor = "#f9f9f9";
                botMessage.style.padding = "10px";
                botMessage.textContent = "Coze: " + botMessages;
                chatMessages.appendChild(botMessage);

                userInput.value = "";
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } catch (error) {
                console.error('发送消息时出错:', error);
                errorContainer.textContent = '发送消息或获取消息详情时出错: ' + error.message;
            }
        }
    }

    return (
        <div>
            <div className="chat-container">
                <div className="chat-header">Chat</div>
                <div className="chat-messages" id="chat-messages"></div>
                <div className="chat-input">
                    <input type="text" id="user-input" placeholder="Type a message..." />
                    <button onClick={sendMessage}>Send</button>
                </div>
                <div className="response-container" id="response-container" ></div>
                <div className="error-container" id="error-container" ></div>
            </div>
        </div>
    )
}

export default Myai;