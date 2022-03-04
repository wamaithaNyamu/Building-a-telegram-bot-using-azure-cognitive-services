from fpdf import FPDF
import PyPDF2
import os
import random
x = [
    "The Board of Elementary and Secondary Education shall provide leadershi and create policies for education that expand opportunities for children, empower families and communities, and advance Louisiana in an increasingly competitive global market. BOARD of ELEMENTARY and SECONDARY EDUCATION ",
    "hey", "I LOVE YOU", "CHOOKKssss", "something else begins right here with this guy!"]

intro=["PDF generated from images"]


def save_to_pdf(pdf_name,results):

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    r = ' '.join(str(e) for e in results)
    for t in r.split('\n'):
        pdf.write(8, t)
        pdf.ln(8)
    pdf.output(pdf_name, 'F')


def add_to_pdf(pdf_name,results):
    if not os.path.exists(pdf_name):
        save_to_pdf(pdf_name,intro)
        pdf1File = open(pdf_name, 'rb')
    temp = f'{random.randint(0,100)}.pdf '
    save_to_pdf(temp, results)

    pdf2File = open(temp, 'rb')
    pdf1Reader = PyPDF2.PdfFileReader(pdf1File)
    pdf2Reader = PyPDF2.PdfFileReader(pdf2File)
    pdfWriter = PyPDF2.PdfFileWriter()

    for pageNum in range(pdf1Reader.numPages):
        pageObj = pdf1Reader.getPage(pageNum)
        pdfWriter.addPage(pageObj)
    for pageNum in range(pdf2Reader.numPages):
        pageObj = pdf2Reader.getPage(pageNum)
        pdfWriter.addPage(pageObj)

    pdfOutputFile = open(pdf_name, 'wb')
    pdfWriter.write(pdfOutputFile)
    pdfOutputFile.close()
    pdf1File.close()
    pdf2File.close()
    os.remove(temp)

add_to_pdf("Hey.pdf",x)
