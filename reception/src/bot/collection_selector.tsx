import React from 'react';
import { useEffect, useState } from 'react';
import { Select, Space } from 'antd';



const getCollectionsUrl = process.env.REACT_APP_GETCOLLECTIONS
const handleChange = (value: string) => {
    console.log(`selected ${value}`);
};


//定义一个接口,用来做状态提升的，将选中的collection传递给父组件
interface NotifyCollection {
    //这个接口的属性是一个函数，函数的参数是any类型，返回值是void
    notify: (response: any) => void;
}

const CollectionSelector: React.FC<NotifyCollection> = ({ notify }) => {

    // 记录所有的collection
    const [collections, setCollections] = useState<string[]>([]);
    // 记录当前选中的collection
    const [selectedCollection, setSelectedCollection] = useState<string>('');
    useEffect(() => {
        console.log(getCollectionsUrl)
        fetch(getCollectionsUrl)
            .then(response => response.json())
            .then(data => {
                console.log(data)
                setCollections(data)

            })
    }, [])

    const handleChange = (value: string) => {
        console.log(`selected ${value}`);
        setSelectedCollection(value);
        notify(value);
    };
    return (<Space wrap>
        <Select

            style={{ width: 120 }}
            onChange={handleChange}
            options={collections.map((collection) => ({ value: collection, label: collection }))}
        />
    </Space>)
};

export default CollectionSelector;