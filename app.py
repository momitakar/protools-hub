from flask import Flask, render_template, request, send_file
import os
from PIL import Image
import io
from PyPDF2 import PdfMerger

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/age-calculator')
def age_calculator():
    return render_template('age_calculator.html')

@app.route('/bmi-calculator')
def bmi_calculator():
    return render_template('bmi_calculator.html')

@app.route('/password-generator')
def password_generator():
    return render_template('password_gen.html')

# Image Compressor & Converter Route
@app.route('/image-tool', methods=['GET', 'POST'])
def image_tool():
    if request.method == 'POST':
        file = request.files.get('image')
        if not file or file.filename == '':
            return "Please select an image file."
            
        action = request.form.get('action') # 'compress' or 'convert'
        target_format = request.form.get('format', 'JPEG').upper()
        
        try:
            img = Image.open(file.stream)
            output = io.BytesIO()
            img_format = img.format if img.format else 'JPEG'
            
            if action == 'compress':
                save_format = img_format.upper()
                if save_format in ['JPEG', 'JPG'] and img.mode in ('RGBA', 'P', 'LA'):
                    img = img.convert('RGB')
                    save_format = 'JPEG'
                elif img.mode not in ('RGB', 'L') and save_format != 'PNG':
                    img = img.convert('RGB')
                    
                img.save(output, format=save_format, quality=50, optimize=True)
                output.seek(0)
                
                ext = 'jpeg' if save_format in ['JPEG', 'JPG'] else save_format.lower()
                return send_file(output, mimetype=f'image/{ext}', as_attachment=True, download_name=f"compressed_{file.filename}")
            
            elif action == 'convert':
                if img.mode in ("RGBA", "P") and target_format in ["JPEG", "JPG"]:
                    img = img.convert("RGB")
                elif img.mode not in ("RGB", "L") and target_format == "JPEG":
                    img = img.convert("RGB")
                    
                img.save(output, format=target_format, quality=85)
                output.seek(0)
                ext = 'jpeg' if target_format in ['JPEG', 'JPG'] else target_format.lower()
                return send_file(output, mimetype=f'image/{ext}', as_attachment=True, download_name=f"converted.{ext}")
                
        except Exception as e:
            return f"Error processing image: {str(e)}"
            
    return render_template('image_tool.html')

# PDF Merger Route
@app.route('/pdf-merger', methods=['GET', 'POST'])
def pdf_merger():
    if request.method == 'POST':
        files = request.files.getlist('pdf_files')
        if len(files) < 2:
            return "Please upload at least 2 PDF files to merge."
        
        merger = PdfMerger()
        for file in files:
            merger.append(file.stream)
            
        output = io.BytesIO()
        merger.write(output)
        merger.close()
        output.seek(0)
        
        return send_file(output, mimetype='application/pdf', as_attachment=True, download_name="merged_document.pdf")
        
    return render_template('pdf_tool.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)