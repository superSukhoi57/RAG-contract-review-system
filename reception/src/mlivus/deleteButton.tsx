import React from 'react';
import type { PopconfirmProps } from 'antd';
import { Button, message, Popconfirm } from 'antd';

//引入.env文件中的环境变量
const dropurl = process.env.REACT_APP_DELCOLLECTION;
console.log('dropcol:', dropurl);
const confirm: PopconfirmProps['onConfirm'] = (e) => {
    console.log(e);
    message.success('删除成功');
};

const cancel: PopconfirmProps['onCancel'] = (e) => {
    console.log(e);
    message.error('取消删除');
};

interface DeleteProps {
    item: string; // 根据实际的 item 类型进行调整
}

const DeleteButton: React.FC<DeleteProps> = ({ item }) => {
    var url = dropurl + '?collectioname='

    const dropcol = () => {
        url += item;
        console.log('url:', url);
        console.log("======================================")
        fetch(url, {
            method: 'DELETE',
        })
            .then((response) => {
                if (response.status === 200) {
                    message.success('删除成功');
                    window.location.reload();
                }
            })
    };

    return (<Popconfirm
        title="删除集合！"
        description="Are you sure to delete this collection?"
        onConfirm={dropcol}
        onCancel={cancel}
        okText="确定"
        cancelText="取消"
    >
        <Button danger >删除</Button>
    </Popconfirm>)
};

export default DeleteButton;