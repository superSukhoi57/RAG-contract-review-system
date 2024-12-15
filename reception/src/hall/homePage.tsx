import React, { useState } from 'react';
import {
    DesktopOutlined,
    FileOutlined,
    PieChartOutlined,
    TeamOutlined,
    UserOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { Layout, Menu, theme } from 'antd';


import Myupload from '../pages/upload.tsx';
import Showpdf from '../pages/showpdf';
import Myai from '../bot/myAi';
import LLLM from '../bot/baichuan.tsx';
import LLLM1 from '../bot/baichuan1.tsx';
import StreamChat from '../bot/baichuan2.tsx';
import HandleCollection from '../mlivus/handleCollection.jsx';
import Baichuan3 from '../bot/baichuan3.tsx';
import Baichun4 from '../bot/baichuan4.tsx';


const { Header, Content, Footer, Sider } = Layout;

type MenuItem = Required<MenuProps>['items'][number];

var attu_url = process.env.REACT_APP_ATTU;

function getItem(
    label: React.ReactNode,
    key: React.Key,
    icon?: React.ReactNode,
    children?: MenuItem[],
): MenuItem {
    return {
        key,
        icon,
        children,
        label,
    } as MenuItem;
}

//——————————————————————————————注意这里的items数组，是菜单项的配置———和sortage-system项目的有联系
/**
Menu可以这样  <Menu theme="dark" defaultSelectedKeys={['1']} mode="inline" onClick={onMenuClick}>
                    <Menu.Item key="1" icon={<PieChartOutlined />}>对比审查</Menu.Item>
                    <Menu.Item key="2" icon={<DesktopOutlined />}>Option 2</Menu.Item>
                    </Menu>

 */
const items: MenuItem[] = [
    getItem('对比两篇合同(pdf)', '1', <PieChartOutlined ></PieChartOutlined>),
    getItem('火山Ai助手', '2', <DesktopOutlined />),
    getItem('使用AI', 'sub1', <UserOutlined />, [
        getItem('outdatecntrv', '4'),
        getItem('流式对话', '5'),
        getItem('简单地审查pdf', '6'),
        getItem('用RAG审查pdf', '11'),

    ]),
    getItem('知识库管理', 'sub2', <TeamOutlined />, [
        getItem('集合管理', '7'),
        getItem('<内嵌管理面板>', '9'),
        getItem('<网页管理面板>', '10'),
    ]),
    getItem('Files', '12    ', <FileOutlined />),
];

const App: React.FC = () => {
    const [collapsed, setCollapsed] = useState(false);
    const {
        token: { colorBgContainer, borderRadiusLG },
    } = theme.useToken();

    const [selectedKey, setSelectedKey] = useState('1'); // 默认选中的菜单项

    const onMenuClick = (e: any) => {
        setSelectedKey(e.key); // 更新选中的菜单项
    };

    // ————————————————————根据选中的菜单项渲染内容！————————————————局部渲染的关键代码————————————————————————
    const renderContent = () => {
        switch (selectedKey) {
            case '1':
                return (<div><h2>上传要比对的两份文档</h2>
                    <Myupload />
                    <Showpdf /></div>);
            case '2':
                return <Myai />;
            // 添加更多case来渲染其他内容
            case '3':
                return <LLLM />;
            case '4':
                return <LLLM1 />;
            case '5':
                return <StreamChat />;
            case '7':
                return <HandleCollection />;
            case '6'://pdfreview
                return <Baichuan3 />;
            case '9':
                return (
                    <iframe src="http://127.0.0.1:8002" title='Milvus管理' width="100%" height="100%"></iframe>
                )
            case '10':
                window.location.href = String(attu_url);
                return null;
            case '11':
                return <Baichun4 />;
            default:
                return <div>默认内容</div>;
        }
    };
    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Sider collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)}>
                <div className="demo-logo-vertical" />
                {/* 下面的onClick={onMenuClick}是自己写，绑定事件，组件的代码没给 */}
                <Menu theme="dark" defaultSelectedKeys={['1']} mode="inline" items={items} onClick={onMenuClick} />
            </Sider>
            <Layout>
                <Header style={{ padding: 0, background: colorBgContainer }} />
                <Content style={{ margin: '0 4px' }}>

                    <div
                        style={{
                            padding: 0,
                            minHeight: 360,
                            height: '100%',
                            background: colorBgContainer,
                            borderRadius: borderRadiusLG,
                        }}
                    >
                        {renderContent()}
                    </div>
                </Content>
                <Footer style={{ textAlign: 'center' }}>
                    1626299398@qq.com ©{new Date().getFullYear()} Created by superSukhoi
                </Footer>
            </Layout>
        </Layout>
    );
};

export default App;