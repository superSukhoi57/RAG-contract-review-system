import React, { useState } from 'react';
import { Upload, message } from 'antd';
import { UploadProps } from 'antd/lib/upload';
import { InboxOutlined } from '@ant-design/icons';

//==========接口，规定了组件的props类型。js的接口更像是其他强类型语言的形参表===========
interface OtherComponentProps {
    //这个接口定义了一个名为 OtherComponentProps 的接口。该接口包含一个属性 uploadResponse，类型为 any。
    uploadResponse: any;
}
interface BaichuanUploadProps {
    /*
    这个接口定义了一个名为 BaichuanUploadProps 的接口。
该接口包含一个属性 onUploadResponse，类型为一个函数，该函数接受一个 response 参数，类型为 any，并且没有返回值 (void)。
这个接口可以用来描述一个组件的属性，该组件需要一个 onUploadResponse 回调函数，用于处理上传响应。
    */
    onUploadResponse: (response: any) => void;
}


//============上传子组件================
const baichuan = process.env.REACT_APP_CNTREVIEW;

//我们自定义的组件，React.FC是React的类型定义文件中定义的一个类型，它代表了一个没有状态（state）和生命周期方法（lifecycle methods）的函数组件。
const BaichuanUpload1: React.FC<BaichuanUploadProps> = ({ onUploadResponse }) => {
    //UploadProps是antd的类型定义文件中定义的一个类型，提供了一系列的属性，用于配置上传组件的行为。
    const props: UploadProps = {
        name: 'file',
        multiple: false,
        action: baichuan,
        onChange(info) {
            const { status } = info.file;
            if (status !== 'uploading') {
                console.log(info.file, info.fileList);
            }
            if (status === 'done') {
                message.success(`${info.file.name} file uploaded successfully.`);
                console.log('Response:', info.file.response); // 获取响应信息
                //实际上这个props可以写在外面，但需要用到组件的回调函数，所以放在里面
                onUploadResponse(info.file.response); // 调用回调函数
            } else if (status === 'error') {
                message.error(`${info.file.name} file upload failed.`);
            }
        },
        onDrop(e) {
            console.log('Dropped files', e.dataTransfer.files);
        },
    };


    //return <Upload {...props}>Upload</Upload>;

    /*
    const { Dragger } = Upload; 这行代码是一个解构赋值的语法，它是ES6（ECMAScript 2015）
    中引入的一种语法，用于从一个对象中提取出部分属性并赋值给变量。它告诉JavaScript解释器要
    从右侧的Upload对象中提取名为Dragger的属性。后，你就可以直接使用Dragger来访问Upload对象
    中的Dragger属性，而无需每次都写Upload.Dragger。
    */
    const { Dragger } = Upload;//把Dragger抽取出来antd的样式才能生效
    return (
        <div style={{ width: '50%' }}>
            <Dragger {...props}>
                <p className="ant-upload-drag-icon">
                    <InboxOutlined />
                </p>
                <p className="ant-upload-text">拖曳文件到此或点击这里上传文件</p>
                <p className="ant-upload-hint">
                    每次只能上传一个文件，最好不要上传公司的私密数据或其他受限文件
                </p>
            </Dragger>
        </div>
    );
};




//============其他子组件================
const OtherComponent: React.FC<OtherComponentProps> = ({ uploadResponse }) => {
    return (
        <span>
            <h1>Upload Response:</h1>
            <p>{JSON.stringify(uploadResponse, null, 2)}</p>
        </span>
    );
};

//==============父组件================
const ParentComponent: React.FC = () => {
    const [uploadResponse, setUploadResponse] = useState(null);

    const handleUploadResponse = (response: any) => {
        setUploadResponse(response);
    };

    return (
        <div>
            <BaichuanUpload1 onUploadResponse={handleUploadResponse} />
            <OtherComponent uploadResponse={uploadResponse} />
        </div>
    );
};




export default ParentComponent;