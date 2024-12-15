import React, { useState } from 'react';
import { Button, Modal } from 'antd';
import { CloudUploadOutlined } from '@ant-design/icons';
import InputNum from './inputNum.tsx';


const embedurl = process.env.REACT_APP_EMBEDPDF;
console.log(embedurl);

interface BaichuanUploadProps {
    setMyPdf: (response: any) => void;
}



const PDFupload: React.FC<BaichuanUploadProps> = ({ setMyPdf }) => {


    /* const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            setMyPdf(file);
        }
    } */
    //箭头函数写多了，这里用普通函数
    function handleChange(event: React.ChangeEvent<HTMLInputElement>) {

        const file = event.target.files?.[0];
        if (file) {
            setMyPdf(file);

        }
    }


    return (
        <div style={{ width: '50%' }}>
            <div>
                <CloudUploadOutlined style={{ fontSize: '50px' }} />
                <input type="file" id="file" name="file" onChange={handleChange} />
            </div>
        </div>
    );
};
//========================================================================
interface ModalBtnProps {
    collection: string;
}


const ModalBtn: React.FC<ModalBtnProps> = ({ collection }) => {
    const [modal2Open, setModal2Open] = useState(false);
    const [size, mysetSize] = useState(100);
    const [overlap, mysetOverlap] = useState(50);
    const [pdf, setPdf] = useState<File | null>(null);


    function OK() {
        setModal2Open(false);
        console.log(`参数：size=${size}, overlap=${overlap}, pdf=${pdf?.name}\n开始上传数据`);
        //上传数据，以form-data的形式上传
        const formData = new FormData();
        if (pdf) {
            formData.append('file', pdf);
        }
        //加入collection
        formData.append('collection_name', collection);
        //加入size
        formData.append('size', size.toString());
        //加入overlap
        formData.append('overlap', overlap.toString());
        console.log('formData:', formData);
        //发送数据
        fetch(embedurl, {
            method: 'POST',
            body: formData
        }).then((response) => {
            if (response.status === 200) {
                alert('上传成功');
            }
        })

    }

    return (
        <>
            <Button type="primary" onClick={() => setModal2Open(true)}>
                选中
            </Button>
            <Modal
                title={"选择 " + collection + " 制作知识库"}
                centered // style={{ top: 20 }}可以设置位置
                open={modal2Open}
                //这个就是ok按钮，点击它要上传文件
                onOk={OK}
                onCancel={() => setModal2Open(false)}
            >
                <InputNum setSize={mysetSize} setOverlap={mysetOverlap} />
                <PDFupload setMyPdf={setPdf} />
            </Modal>
        </>
    );
};

export default ModalBtn;