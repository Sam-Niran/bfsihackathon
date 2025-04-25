# Automated Personal Loan Document Processor

This project is an OCR-powered solution for automating personal loan document processing. It extracts key information such as name, date of birth, and address from uploaded documents like PDFs or scanned images. Users can review and edit the extracted data via a simple Streamlit interface, and submit it to a backend system for database storage.

## Problem Statement

Banks receive thousands of personal loan applications daily, each containing documents that must be manually verified and entered into systems. This process is tedious, time-consuming, and error-prone. The goal of this project is to automate data extraction from these documents using OCR, ensuring faster and more reliable processing.

## Features

- Upload multiple documents (pdf, jpg, png, jpeg)
- Extract name, date of birth, and address using Tesseract OCR
- Edit extracted data before final submission
- Save verified information to a MySQL database
- Backend service handles processing and storage via Flask API

## Tech Stack

- Frontend: Streamlit
- Backend: Flask
- OCR Engine: Tesseract OCR
- Database: MySQL
- Other Tools: OpenCV, PIL, Pandas, Regex

## How It Works

1. User uploads documents via Streamlit interface
2. Frontend sends files to Flask backend (`/process-documents`)
3. Backend preprocesses images and extracts text using Tesseract
4. Name, DOB, and Address are parsed using regex and heuristics
5. Extracted data is sent back to frontend for review
6. On confirmation, frontend sends data to another backend route (`/submit-data`)
7. Data is stored in the `user_details` table in MySQL


