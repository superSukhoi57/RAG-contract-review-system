import React from 'react';
import { InboxOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { message, Upload } from 'antd';


const { Dragger } = Upload;
let uploadurl = process.env.REACT_APP_UPLOADURL
uploadurl = uploadurl + "/upload"
console.log(uploadurl)

//使用 TypeScript 语言编写的，定义了一个 props 常量，该常量的类型为 UploadProps，然后将这个常量传递给 Dragger 组件。
const props: UploadProps = {
    name: 'file',
    multiple: true,
    action: uploadurl,
    onChange(info) {
        const { status } = info.file;
        if (status !== 'uploading') {
            console.log(info.file, info.fileList);
        }
        if (status === 'done') {
            message.success(`${info.file.name} 上传成功.`);
        } else if (status === 'error') {
            message.error(`${info.file.name} 上传失败.`);
        }
    },
    onDrop(e) {
        console.log('Dropped files', e.dataTransfer.files);
    },
};
/**
name: 'file'：这个属性设置了上传文件时表单字段的名称，在发送到服务器的请求中，文件的键名将默认为 file。
multiple: true：这个属性表示是否支持多选文件，设置为 true 时，用户可以选择多个文件进行上传。
action: 'https://660d2bd96ddfa2943b33731c.mockapi.io/api/upload'：这个属性定义了上传的服务器端接口地址。文件将会被上传到这个 URL。

onChange(info) { ... }：这是一个事件处理函数，当上传组件的文件状态发生变化时会被触发。info 参数是一个对象，包含了当前操作文件的信息和文件列表。
const { status } = info.file;：通过解构赋值获取文件的上传状态。
if (status !== 'uploading') { ... }：如果文件的状态不是上传中，就打印当前文件和文件列表的信息。
if (status === 'done') { ... }：如果文件上传成功，使用 message.success 方法显示成功提示，其中包含了上传成功的文件名。
else if (status === 'error') { ... }：如果文件上传失败，使用 message.error 方法显示错误提示，其中包含了上传失败的文件名。
onDrop(e) { ... }：这是一个事件处理函数，当用户将文件拖拽到上传区域并释放时会被触发。e 参数是一个事件对象。
console.log('Dropped files', e.dataTransfer.files);：在控制台打印被拖拽的文件列表。
 */


const App: React.FC = () => (
    <Dragger {...props}>
        <p className="ant-upload-drag-icon">
            <InboxOutlined />
        </p>
        <p className="ant-upload-text">单击上传或者将文件拖进来</p>
        <p className="ant-upload-hint">
            Support for a single or bulk upload. Strictly prohibited from uploading company data or other
            banned files.
        </p>
    </Dragger>
);

export default App;