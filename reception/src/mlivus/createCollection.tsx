import React, { useState } from 'react';
import { Button, Modal, InputNumber, Space } from 'antd';
import type { InputNumberProps } from 'antd';

const createUrl = process.env.REACT_APP_CREATECOLLECTION;

const CreateCollection: React.FC = () => {

    const [modalOpen, setModalOpen] = useState(false);

    const [name, setName] = useState('');
    const [dim, setDim] = useState(1024);
    const [capacity, setCapacity] = useState(4096);
    const [nlist, setNlist] = useState(2);

    /*
    在 TypeScript 中，InputNumberProps['onChange'] 是一种类型注解，用于指定 changeOverlap 函数的类型。具体来说，
    它表示 changeOverlap 函数的类型与 InputNumberProps 接口中的 onChange 属性的类型相同。
    */
    const changeSize: InputNumberProps['onChange'] = (value) => {
        console.log('changed size', value);
        setDim(value ?? 1024);//这里的??是空值合并运算符，表示如果value是null或者undefined，就使用1024
    };

    const changeCapacity: InputNumberProps['onChange'] = (value) => {
        console.log('changed overlap', value);
        setCapacity(value ?? 3060);
    };


    const changeNlist: InputNumberProps['onChange'] = (value) => {
        console.log('changed nlist', value);
        setNlist(value ?? 2);
    };

    function create() {
        console.log(`创建Collection，向量维度：${dim}，分片容量：${capacity}`);
        fetch(createUrl, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                dim: dim,
                max_length: capacity,
                nlist: nlist,
            }),
        })
            .then(response => response.json())
            .then(data => {
                console.log(data)
            })
            .catch((error) => {
                console.error('Error:', error);
            });

        setModalOpen(false);
    }
    return (
        <>
            <Button type="primary" onClick={() => setModalOpen(true)}>
                创建Collection
            </Button>

            {/* TODO：Modal就是打开的对话框！！ */}
            <Modal
                title={"一键创建Collection"}
                centered // style={{ top: 20 }}可以设置位置
                open={modalOpen}
                //这个就是ok按钮，点击它要上传文件
                onOk={create}
                onCancel={() => setModalOpen(false)}
            >
                集合名称：<input type="text" onChange={(e) => setName(e.target.value)} />
                <Space direction="vertical" wrap>
                    向量维度：
                    <InputNumber size="large" min={1} max={100000} defaultValue={1024} onChange={changeSize} />
                    分片容量：
                    <InputNumber size="large" min={1} max={100000} defaultValue={3060} onChange={changeCapacity} />
                    nlist：
                    <InputNumber size="large" min={1} max={100000} defaultValue={2} onChange={changeNlist} />
                </Space>
            </Modal>
        </>
    )

}


export default CreateCollection;
