import React, { useEffect, useState } from 'react';


let pdfurl = process.env.REACT_APP_UPLOADURL
pdfurl = pdfurl + '/pdf'

function App() {
    const [pdfUrl, setPdfUrl] = useState('');

    async function compare() {
        await fetch(pdfurl)
            .then(response => response.blob())
            .then(blob => {
                const url = URL.createObjectURL(blob);
                console.log(url);
                setPdfUrl(url);
            });
    }

    return (

        <div >
            <div><button onClick={compare} >开始对比</button></div>

            {pdfUrl && <embed src={pdfUrl} type="application/pdf" style={{ width: '80%', height: '80vh' }} />}
        </div>
    );
}

export default App;