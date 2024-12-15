package com.test.myTools;

import com.spire.pdf.PdfDocument;
import com.spire.pdf.comparison.PdfComparer;


//TODO：这个组件的路径是相对项目的根目录的！！！
public class pdfCompare {
    public static void main(String[] args) {
        //创建一个PdfDocument类对象并加载一个PDF文档
        PdfDocument pdf1 = new PdfDocument();
        pdf1.loadFromFile("./src/main/resources/repository/raw/contract1.5.pdf");

        //创建另一个PdfDocument类对象并加载另一个PDF文档
        PdfDocument pdf2 = new PdfDocument();
        pdf2.loadFromFile("./src/main/resources/repository/raw/contract2.5.pdf");

        //创建一个PdfComparer类的对象
        PdfComparer comparer = new PdfComparer(pdf1, pdf2);

        //比较两个PDF 档并将比较结果保存到一个新文档中
        comparer.compare("./src/main/resources/repository/processed/比较结果1.5.pdf");
    }
}
