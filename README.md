# 🎓 Student Management System

A web-based **Student Management System** developed using Python, Flask, HTML, CSS, and Oracle Database. The application provides a simple interface to manage student information efficiently.

## 📌 Project Overview

The Student Management System is designed to simplify student record management. It allows administrators to add, view, search, update, and delete student records through a web interface.

The project uses **Flask** as the web framework and **Oracle Database** for storing student information.

## ✨ Features

* 🔐 Admin login system
* ➕ Add new student records
* 📋 View all registered students
* 🔍 Search student records
* ✏️ Update existing student information
* 🗑️ Delete student records
* 📄 View individual student details
* 📊 Dashboard with student statistics
* 🗄️ Oracle Database integration

## 🛠️ Technologies Used

| Technology      | Purpose                                  |
| --------------- | ---------------------------------------- |
| Python          | Backend programming                      |
| Flask           | Web application framework                |
| HTML            | Web page structure                       |
| CSS             | User interface styling                   |
| Oracle Database | Data storage                             |
| `oracledb`      | Python connectivity with Oracle Database |
| Jinja2          | Dynamic HTML templates                   |

## 📂 Project Structure

```text
Student_Management_System/
│
├── app.py
├── app_oracle.py
├── .gitignore
├── requirements.txt
│
└── templates/
    ├── login.html
    ├── dashboard.html
    ├── students.html
    ├── add_student.html
    ├── student_details.html
    └── edit_student.html
```

*Note: Your actual files may differ slightly from this structure.*

## ⚙️ Requirements

Before running the application, install the following:

* Python 3.10 or later
* Oracle Database with a configured database service
* pip (Python package manager)

## 🚀 Installation and Setup

### 1. Clone the Repository

Replace `YOUR-USERNAME` with your GitHub username.

```bash
git clone https://github.com/YOUR-USERNAME/Student-Management-System.git
```

### 2. Open the Project Folder

```bash
cd Student-Management-System
```

### 3. Create a Virtual Environment

**Windows:**

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install Flask oracledb
```

Alternatively, if a `requirements.txt` file is provided:

```bash
pip install -r requirements.txt
```

### 5. Configure Oracle Database

Make sure Oracle Database is running and your database service is accessible.

Configure the following environment variables with your own Oracle credentials:

```text
ORACLE_USER=your_oracle_username
ORACLE_PASSWORD=your_oracle_password
ORACLE_DSN=localhost:1521/XEPDB1
```

Do not upload your actual database password to GitHub.

### 6. Run the Application

To run the Oracle Database version:

```bash
python app_oracle.py
```

Open your br
