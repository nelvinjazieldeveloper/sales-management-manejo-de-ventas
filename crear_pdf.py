from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        if hasattr(self, 'document_title'):
            self.set_font('Arial', 'B', 12)
            self.cell(0,10,self.document_title, 0, 1, 'C')
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0,10,'Page '+str(self.page_no()), 0, 0, 'C')
        
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0,10,title, 0, 1, 'C')
        self.ln()
        
    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, body)
        self.ln()

def crear_pdf(filename, document_title, author, chapters, image_path = None):
    pdf = PDF()
    pdf.add_page()
    if author:
        pdf.author = author
    if image_path:
        pdf.image(image_path, x = None, y = None, w = 0, h = 0, type = '', link = '')
        pdf.ln(120)
    for chapter in chapters:
        pdf.chapter_title(chapter['title'])
        pdf.chapter_body(chapter['body'])
    pdf.output(filename)