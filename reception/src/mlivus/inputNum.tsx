import React from 'react';
import type { InputNumberProps } from 'antd';
import { InputNumber, Space } from 'antd';


interface Props {
    setSize: (response: any) => void;
    setOverlap: (response: any) => void;
}


const InputNum: React.FC<Props> = ({ setSize, setOverlap }) => {


    const changeSize: InputNumberProps['onChange'] = (value) => {
        console.log('changed size', value);
        setSize(value);
    };

    const changeOverlap: InputNumberProps['onChange'] = (value) => {
        console.log('changed overlap', value);
        setOverlap(value);
    };

    //direction="vertical"这个属性是设置子元素的排列方向，这里设置为垂直排列
    return (<Space direction="vertical" wrap>

        分片大小：
        <InputNumber size="large" min={1} max={100000} defaultValue={100} onChange={changeSize} />
        Overlap：
        <InputNumber size="large" min={1} max={100000} defaultValue={50} onChange={changeOverlap} />


    </Space>)
}

export default InputNum;