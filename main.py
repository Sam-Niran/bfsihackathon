from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import pytesseract
import cv2
import numpy as np
import io
import re
from datetime import datetime
import mysql.connector

pytesseract.pytesseract.tesseract_cmd = r'F:\tesseract\tesseract.exe'

app = Flask(__name__)
CORS(app)

# --------------------------- MySQL Insert ---------------------------

def insert_into_mysql(data):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="hackathon"
        )
        cursor = connection.cursor()
        sql = """
            INSERT INTO user_details (name, date_of_birth, address)
            VALUES (%s, %s, %s)
        """
        for record in data:
            cursor.execute(sql, (record['Name'], record['DOB'], record['Address']))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except mysql.connector.Error as e:
        print(f"MySQL Error: {e}")
        return False

# --------------------------- Extractors ---------------------------

def extract_name(text):
    lines = text.splitlines()
    name = "n/a"
    for i, line in enumerate(lines):
        if re.search(r'\bName\b', line, re.IGNORECASE):
            for j in range(i + 1, min(i + 3, len(lines))):
                line_text = lines[j].strip()
                if not re.search(r'father|dob|date|birth|signature', line_text, re.IGNORECASE):
                    name_words = re.findall(r'\b[A-Z]{2,}(?:\s+[A-Z]{2,})*\b', line_text)
                    if name_words:
                        name = " ".join(name_words)
                        return name
    return name

def extract_dob(text):
    dob_keywords = r'(?:date|pate|dare|bate)\s+of\s+birth'
    match = re.search(rf'{dob_keywords}[\s:;-]*?(\d{{2}}[-/]\d{{2}}[-/]\d{{4}})', text, re.IGNORECASE)
    if match:
        try:
            dob = datetime.strptime(match.group(1).replace('/', '-'), "%d-%m-%Y")
            return dob.strftime("%Y-%m-%d")
        except ValueError:
            return "n/a"
    possible_dates = re.findall(r'\b(\d{2}[-/]\d{2}[-/]\d{4})\b', text)
    for date_str in possible_dates:
        try:
            dob = datetime.strptime(date_str.replace('/', '-'), "%d-%m-%Y")
            return dob.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return "n/a"

def extract_address(text):
    match = re.search(r'Address\s*[:\-]?\s*([A-Za-z0-9\s,.-]+(?:\n[A-Za-z0-9\s,.-]+)*)', text, re.IGNORECASE)
    return match.group(1).strip() if match else "n/a"

# --------------------------- Image Preprocessing ---------------------------

def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    open_cv_image = np.array(image)
    img = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)

    h, w = img.shape[:2]
    if w < 800 or h < 800:
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(denoised)
    _, binary = cv2.threshold(contrast, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((1, 1), np.uint8)
    morphed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    return morphed

# --------------------------- Routes ---------------------------

@app.route('/process-documents', methods=['POST'])
def process_documents():
    results = []
    files = request.files.getlist('files')
    for file in files:
        contents = file.read()
        processed_image = preprocess_image(contents)
        text = pytesseract.image_to_string(processed_image)
        print("----- Extracted Text -----")
        print(text)
        results.append({
            "name": extract_name(text),
            "dateOfBirth": extract_dob(text),
            "address": extract_address(text)
        })
    return jsonify(results)

@app.route('/submit-loan-data', methods=['POST'])
def submit_loan_data():
    data = request.get_json()
    if not data or not isinstance(data, list):
        return jsonify({"error": "Invalid payload"}), 400

    success = insert_into_mysql(data)
    if success:
        return jsonify({"message": "Data inserted successfully"}), 200
    else:
        return jsonify({"error": "Failed to insert into database"}), 500

# --------------------------- Run App ---------------------------

if __name__ == '__main__':
    app.run(debug=True)
