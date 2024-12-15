import React, { useState } from 'react';
import { InboxOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { message, Upload } from 'antd';

/*
const { Dragger } = Upload; 这行代码是一个解构赋值的语法，它是ES6（ECMAScript 2015）
中引入的一种语法，用于从一个对象中提取出部分属性并赋值给变量。它告诉JavaScript解释器要
从右侧的Upload对象中提取名为Dragger的属性。后，你就可以直接使用Dragger来访问Upload对象
中的Dragger属性，而无需每次都写Upload.Dragger。
*/
const { Dragger } = Upload;

const baichuan = process.env.REACT_APP_BAICHUANURL;
console.log(baichuan);

console.log("start")

/*
props: UploadProps 是 TypeScript 中的一种类型注解，用于指定 props 的类型为 UploadProps。
这通常出现在类组件或函数组件的定义中，用于确保传递给组件的 props 符合 UploadProps 接口的
定义。
*/
const props: UploadProps = {
  name: 'file',
  multiple: false,
  action: baichuan, // 使用相对路径
  onChange(info) {
    const { status } = info.file;
    if (status !== 'uploading') {
      console.log(info.file, info.fileList);
    }
    if (status === 'done') {
      message.success(`${info.file.name} file uploaded successfully.`);
      console.log('Response:', info.file.response); // 获取响应信息
    } else if (status === 'error') {
      message.error(`${info.file.name} file upload failed.`);
    }
  },
  onDrop(e) {
    console.log('Dropped files', e.dataTransfer.files);
  },
};

const BaichuanUpload = () => (
  <Dragger {...props}>
    <p className="ant-upload-drag-icon">
      <InboxOutlined />
    </p>
    <p className="ant-upload-text">Click or drag file to this area to upload</p>
    <p className="ant-upload-hint">
      Support for a single or bulk upload. Strictly prohibit from uploading company data or other
      band files
    </p>
  </Dragger>
);


export default BaichuanUpload;