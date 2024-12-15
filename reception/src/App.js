import Myupload from './pages/upload.tsx';
import HomePage from './hall/homePage.tsx'
//tsx在导入时要写明后缀名
import './App.css';
import Showpdf from './pages/showpdf';
function App() {
  return (
    <div className="App">
      {/*  <h2>上传要比对的两份文档</h2>
      <Myupload />
      <Showpdf /> */}
      <HomePage />
    </div>
  );
}

export default App;
