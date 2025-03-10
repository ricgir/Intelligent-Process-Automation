# Intelligent-Process-Automation

## Overview
This project automates the extraction and processing of invoice data from invoice images and PDFs. It utilizes **Pytesseract** to extract text from invoice images (PNG, JPG, JPEG) and **pdfplumber** to extract text from PDFs. The extracted text is then passed to the **Gemini-1.5-Pro** model via the Gemini API, which processes the text and structures the information into a JSON format. The structured data is subsequently stored in a **PostgreSQL** database deployed on **Railway** (`railway`) within the `invoices` table. The entire application runs within a **Python virtual environment** (`invoice virtual environment`) to ensure dependency isolation and maintainability.


## Features
- Extracts text from invoice images using **Pytesseract**.
- Extracts text from PDF invoices using **pdfplumber**.
- Processes and structures extracted text into JSON using **Gemini-1.5-Pro**.
- Stores structured invoice data in a **PostgreSQL** database deployed on **Railway**.
- Runs within a Python virtual environment for better dependency management.
---

## Setup and Installation

### **1. Clone the Repository**
To get started, clone the repository and navigate into the project directory:
```sh
 git clone https://github.com/ricgir/Intelligent-Process-Automation.git
 cd Intelligent-Process-Automation
```

### **2. Set Up the Virtual Environment**
It is recommended to run the application inside a virtual environment to avoid conflicts between dependencies.
```sh
python3 -m venv invoice
source invoice/bin/activate  # On Windows, use `invoice\Scripts\activate`
```

### **3. Install Dependencies**
Install the necessary dependencies from the `requirements.txt` file:
```sh
cd invoice
pip install -r requirements.txt
```

---

## Running the Application

### **1. Activate the Virtual Environment**
Before running the application, ensure the virtual environment is activated:
```sh
source invoice/bin/activate  # On Windows, use `invoice\Scripts\activate`
cd invoice
```

### **2. Run the Application**
To start processing invoices, run the main application script:
```sh
python app.py
```

---

## Viewing Stored Data in PostgreSQL

### **1. Access the Database**
To interact with the database and view stored invoices, access PostgreSQL:
```sh
psql "postgresql://postgres:lKyPkdyoIkhLCpUgaMNgVYZbmsdJGAAo@hopper.proxy.rlwy.net:15298/railway"
```

### **2. View Stored Invoices**
Retrieve all stored invoice records:
```sql
SELECT * FROM invoices;
```

### **3. Query Specific Data**
To filter invoices by date or invoice number:
```sql
SELECT * FROM invoices WHERE date = '2025-01-01';
SELECT * FROM invoices WHERE invoice_number = 'INV-1001';
```

---

## Troubleshooting

### **Common Issues & Fixes**

- **Virtual environment not activating:** Use the correct command for your OS (`source invoice/bin/activate` on macOS/Linux, `invoice\Scripts\activate` on Windows).
- **Missing dependencies:** Run `pip install -r requirements.txt` to reinstall required packages.

---

## Contributing
We welcome contributions! Fork the repository, create a feature branch, and submit a pull request.

---

## License
This project is licensed under the MIT License.
