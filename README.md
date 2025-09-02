# 📚 Fajao Exam Bank

**Bridging the Educational Divide, One Exam Paper at a Time**

> A digital platform making quality exam materials accessible to every student in Kenya, especially those in rural and marginalized communities.

![Fajao Exam Bank Preview](https://img.shields.io/badge/Status-In%20Development-orange) ![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Flask](https://img.shields.io/badge/Flask-2.3-green) ![MySQL](https://img.shields.io/badge/MySQL-8.0-lightgrey)

---

## 🚀 What's in the Box?

A full-stack web application built to democratize education:

*   **🌐 Frontend:** Beautiful, responsive website for searching and downloading exams
*   **⚙️ Backend:** Robust Flask API handling authentication, uploads, and payments
*   **🗄️ Database:** MySQL database storing users, exams, and payment records
*   **💸 Monetization:** IntaSend integration for M-Pesa and card payments

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **🔍 Smart Search** | Find exams by subject, form, year, or keyword |
| **🆓✨ Dual Access** | Free foundational content & premium library for subscribers |
| **👩‍🏫📤 Teacher Empowerment** | Educators can upload materials and contribute |
| **🇰🇪 Kenyan-First** | Built for the Kenyan curriculum (8-4-4 & CBC) |
| **📶 Low-Bandwidth Friendly** | Works well in areas with limited internet |

---

## 🛠️ Tech Stack

*   **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
*   **Backend:** Python, Flask, Flask-JWT-Extended
*   **Database:** MySQL
*   **File Storage:** Local file system (easily upgradable to AWS S3)
*   **Payments:** IntaSend API (M-Pesa, Cards, Bank)
*   **Deployment:** Ready for Heroku, AWS, or Linux VPS

---

## 🚦 Quick Start

Get this project running on your local machine in 5 minutes!

### Prerequisites

*   Python 3.8+
*   MySQL Server
*   Modern web browser

### Installation & Setup

1.  **Clone the repo:**
    ```bash
    git clone https://github.com/your-username/fajao-exam-bank.git
    cd fajao-exam-bank
    ```

2.  **Set up your Python environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configure your database:**
    ```sql
    CREATE DATABASE fajao_exam_bank_db;
    CREATE USER 'fajao_user'@'localhost' IDENTIFIED BY 'securepassword';
    GRANT ALL PRIVILEGES ON fajao_exam_bank_db.* TO 'fajao_user'@'localhost';
    FLUSH PRIVILEGES;
    ```

4.  **Update database configuration in `app.py`:**
    ```python
    db_config = {
        'host': 'localhost',
        'user': 'fajao_user',
        'password': 'securepassword',
        'database': 'fajao_exam_bank_db'
    }
    ```

5.  **Run the application:**
    ```bash
    python app.py
    ```

6.  **Open your browser** and go to `http://localhost:5000`

---

## 🧩 Project Structure
fajao-exam-bank/
├── app.py # Main Flask application
├── requirements.txt # Python dependencies
├── uploads/ # Directory for uploaded exam files
├── static/ # CSS, JS, and images
│ ├── css/
│ └── js/
├── templates/ # HTML templates
│ └── index.html # Main frontend page
└── README.md # This file

text

---

## 🧪 Sample Data

After setting up, you can add sample data to your database:

```sql
USE fajao_exam_bank_db;

INSERT INTO users (name, email, password_hash, is_premium) VALUES
('John Doe', 'john@example.com', 'password123', 1),
('Jane Smith', 'jane@example.com', 'password123', 0);

INSERT INTO exams (title, subject, form_level, exam_type, is_premium, filename, file_size, file_type, uploaded_by) VALUES
('Mathematics Form 2 Midterm', 'Mathematics', 'Form 2', 'Midterm', 0, 'math_form2_midterm.pdf', 245000, 'PDF', 1),
('English Form 3 Composition', 'English', 'Form 3', 'Assignment', 1, 'english_form3_composition.pdf', 187000, 'PDF', 2);
🤝 How to Contribute
We love contributions! Here's how you can help:

Fork the project

Create a Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

Looking for ideas?

Add a feature to favorite exams

Improve the search algorithm

Build a simple admin dashboard

Write better tests

Translate the UI to Kiswahili

📜 License
This project is licensed under the MIT License - see the LICENSE file for details.

📞 Contact
Have questions or want to collaborate?

Email: contact@fajaobank.co.ke

Twitter: @fajaobank

Website: https://fajaobank.co.ke

🙏 Acknowledgments
Kenyan teachers and students who inspired this project

The Flask community for excellent documentation

IntaSend for making payments integration easier

<div align="center">
⭐ Don't forget to star this repo if you found it useful!

</div> ```
To use this README:

Create a new file named README.md in your project's root directory

Copy and paste the entire content above into this file

Customize the sections with your specific information:

Replace your-username with your actual GitHub username

Update the contact information with your actual details

Add any additional sections specific to your project

This README includes:

Eye-catching badges and emojis

Clear installation instructions

Visual project structure

Contribution guidelines

Sample database queries

Contact information

License details

The formatting uses GitHub Flavored Markdown and will render beautifully on your GitHub repository page.
