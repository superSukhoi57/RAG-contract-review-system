import React, { useState } from 'react';
import { useEffect } from 'react';
import { Upload, message } from 'antd';
import { UploadProps } from 'antd/lib/upload';
import { InboxOutlined } from '@ant-design/icons';
import DeleteButton from './deleteButton.tsx';
import ModalBtn from './modalBtn.tsx';
import CreateCollection from './createCollection.tsx';

const getCollectionsUrl = process.env.REACT_APP_GETCOLLECTIONS
const HandleCollection = () => {



    // 记录所有的collection
    const [collections, setCollections] = useState([]);
    // 记录当前选中的collection
    //const [selectedCollection, setSelectedCollection] = useState<string>('');
    useEffect(() => {
        console.log(getCollectionsUrl)
        fetch(getCollectionsUrl)
            .then(response => response.json())
            .then(data => {
                console.log(data)
                setCollections(data)

            })
    }, [])



    return (
        <div>
            <h1>使用Mlivus</h1>
            <CreateCollection />
            <div>
                {collections.map((item, index) => {
                    return (
                        <span key={index} style={{ fontSize: '2em', display: 'flex', justifyContent: 'space-evenly', backgroundColor: 'ButtonShadow', margin: '1px' }}>
                            <span style={{ width: '50%', textAlign: 'left' }}>{item}</span>
                            <DeleteButton item={item} />
                            <ModalBtn collection={item} />
                        </span>)
                })}

            </div>
        </div>
    );
}

export default HandleCollection;