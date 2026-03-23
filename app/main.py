import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.parser import LogParser
from engine.generator import ReportGenerator

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')

# Use absolute paths relative to project root
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = str(BASE_DIR / 'uploads')
OUTPUT_FOLDER = str(BASE_DIR / 'reports')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def api_generate():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "Vui lòng chọn file!"})
    
    file = request.files['file']
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    if file.filename == '' or not start_date or not end_date:
        return jsonify({"success": False, "error": "Vui lòng điền đầy đủ thông tin!"})
    
    try:
        sd = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d/%m/%Y")
        ed = datetime.strptime(end_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception as e:
        return jsonify({"success": False, "error": f"Lỗi định dạng ngày: {str(e)}"})

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'engine', 'config.json')
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            
        parser = LogParser(filepath)
        parsed_data = parser.parse(sd, ed)
        
        generator = ReportGenerator(sd, ed)
        output_filename = f"bao_cao_tuan_{start_date}_to_{end_date}.docx"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        generator.generate(parsed_data, output_path)
        
        return jsonify({
            "success": True, 
            "data": parsed_data,
            "config": config_data,
            "start_date": sd,
            "end_date": ed,
            "download_url": url_for('download_file', filename=output_filename)
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Lỗi khi xử lý: {str(e)}"})

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(os.path.abspath(OUTPUT_FOLDER), filename), as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5006))
    app.run(debug=False, host='0.0.0.0', port=port)
