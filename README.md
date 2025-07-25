# 🧠 AI-Based Aptitude Exam Portal

## Project Overview
This project is an AI-powered aptitude exam portal built using Streamlit and integrated with the Groq API. It allows users to generate custom aptitude questions, take exams on various topics and difficulties, and track their performance.

## Features
**User Authentication:** Secure user login and registration.
**AI-Powered Question Generation:** Generate aptitude questions based on specified topics and difficulty levels (easy, medium, hard) using the Groq API.
**Dynamic Exam Taking:** Take timed aptitude tests with questions loaded from the database and shuffled options.
**Exam History & Performance Tracking:** View past exam results, including topic, difficulty, score, and percentage.
**Question Management:** Browse, edit, and delete saved questions directly within the application.
**SQLite Database:** Persistent storage for questions, user data, and exam results.

## Technologies Used
**Frontend/Web Framework:** Streamlit
**AI API Integration:** Groq API (using the `llama3-8b-8192` model for question generation) 
**Database:** SQLite3
**Programming Language:** Python 3.9+
**Other Python Libraries:** `python-dotenv` (for environment variables), `hashlib` (for password hashing), `random` (for shuffling), `time` (for timers)

## Installation and Setup

### Prerequisites
Python 3.9 or higher 
Git (for cloning the repository) 
An active internet connection (required for Groq API communication) 
A Groq API Key

### Steps:

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/BhavinKalal/AI-Aptitude-Exam-Portal.git](https://github.com/BhavinKalal/AI-Aptitude-Exam-Portal.git)
    cd AI-Aptitude-Exam-Portal
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (This will install `streamlit` and `groq`).

4.  **Set up Groq API Key:**
    Create a file named `.env` in the root directory of your project (where `app.py` is located).
    Add your Groq API key to this file:
    ```
    GROQ_API_KEY=your_groq_api_key_here
    ```
    (Replace `your_groq_api_key_here` with your actual key from Groq. This is crucial for the AI question generation [cite: 1]).

5.  **Run the Application:**
    ```bash
    streamlit run app.py
    ```
    This will open the application in your default web browser.

## How to Use

1.  **Login/Register:** On the sidebar, register a new account or log in if you already have one.
2.  **Generate Questions:** Navigate to the "Generate Questions" section. Enter a topic, select difficulty, and specify the number of questions to generate. Click "Generate Question(s)". The AI will create and save them to the database.
3.  **Take Exam:** Go to the "Take Exam" section. Choose a topic and difficulty, then click "Start Exam". Answer the questions within the given time limit and submit to see your score and review answers.
4.  **View Saved Questions:** In the "View Saved Questions" section, you can browse all questions in the database, filter them by topic or difficulty, and even edit or delete individual questions.
5.  **Exam History:** Check the "Exam History" section to review your past exam attempts and scores.

## Database Structure
The application uses an SQLite database (`questions.db`) with the following tables:
`users`: Stores user `id`, `username`, and `password` (hashed). 
`questions`: Stores `id`, `topic`, `difficulty`, `question` text, four `option` fields, and the `answer` text.
`exam_results`: Records `id`, `user_id`, `exam_date`, `topic`, `difficulty`, `score`, and `total_questions` for each exam taken.

## Development Environment
**Operating System:** Windows 10/11 (developed on, but portable) 
**IDE:** Visual Studio Code 
**Version Control:** Git

## Contributing
Feel free to fork the repository, open issues, and submit pull requests.

## License
[Consider adding a license, e.g., MIT License]

---

This `README.md` provides a clear and comprehensive overview of your project, its features, how to set it up, and how to use it, all based on the files you've shared.
