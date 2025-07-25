import streamlit as st
from ai_model.question_generator import generate_multiple_questions
from database.db_handler import create_table, insert_question, get_questions, count_questions, get_questions_all, update_question, delete_question_by_id, is_duplicate_question, add_user, verify_user, record_exam_result, get_user_exam_results
import time
import random

create_table()

st.title("🧠 AI-Based Aptitude Exam Portal")

# --- Session state for authentication ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Sidebar for login/logout and user info
st.sidebar.header("User Account")
if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.clear() # Clear all session state on logout
        st.info("Logged out successfully.")
        st.rerun() # Rerun to show login screen
else:
    auth_choice = st.sidebar.radio("Authentication", ["Login", "Register"])
    if auth_choice == "Login":
        with st.sidebar.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                user_id = verify_user(username, password)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_id = user_id
                    st.success(f"Welcome, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
    elif auth_choice == "Register":
        with st.sidebar.form("register_form"):
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            register_button = st.form_submit_button("Register")

            if register_button:
                if new_username and new_password:
                    if add_user(new_username, new_password):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Username already exists. Please choose a different one.")
                else:
                    st.error("Username and password cannot be empty.")

st.sidebar.markdown("---") # Separator

if st.session_state.logged_in:
    st.sidebar.markdown(f"🗃️ Total Questions in DB: **{count_questions()}**")

    menu = ["Generate Questions", "Take Exam", "View Saved Questions", "Exam History"]
    choice = st.sidebar.radio("Menu", menu)

    if choice == "Generate Questions":
        st.header("📌 Generate Aptitude Questions")

        topic = st.text_input("Topic", "percentages")
        difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"])
        num_questions = st.number_input("How many questions to generate?", min_value=1, max_value=20, value=1)

        if st.button("Generate Question(s)"):
            with st.spinner("Generating..."):
                questions_to_process = generate_multiple_questions(topic, difficulty, num_questions)
                success_count = 0

                for q_data in questions_to_process:
                    # q_data should now directly be a dictionary from question_generator.py
                    # with keys 'question', 'options', 'answer'
                    question_text = q_data.get("question")
                    options_list = q_data.get("options")
                    correct_answer_text = q_data.get("answer")

                    # Enhanced UI feedback for generation
                    if question_text and options_list and len(options_list) == 4 and correct_answer_text:
                        if not is_duplicate_question(question_text):
                            insert_question(topic, difficulty, question_text, options_list, correct_answer_text)
                            st.success("✅ Question generated and saved:")
                            st.write("**Question:**", question_text)
                            for opt in options_list:
                                st.write("-", opt)
                            st.write("**Answer:**", correct_answer_text)
                            success_count += 1
                        else:
                            st.warning(f"⚠️ Duplicate question skipped: {question_text[:50]}...") # Show part of the question
                    else:
                        # This warning catches issues from generate_multiple_questions not returning full data
                        st.warning("⚠️ Failed to generate a complete question due to internal parsing issues or incomplete AI response. Please try again or adjust prompt.")

                st.info(f"✅ Total successfully generated and saved questions: {success_count} out of {num_questions} attempts.")
                st.sidebar.markdown(f"🗃️ Updated Total Questions: **{count_questions()}**")

    #--------------------------------------------------------------------------------------------------------------------------------------------------

    elif choice == "Take Exam":
        st.header("📝 Take an Aptitude Test")

        topic = st.text_input("Enter Topic", "percentages")
        difficulty = st.selectbox("Select Difficulty", ["easy", "medium", "hard"])

        # Get questions from DB (this returns tuples as before)
        # We only fetch questions once and store them in session state if they aren't there
        if "current_exam_questions" not in st.session_state or \
            st.session_state.get("current_exam_topic") != topic or \
            st.session_state.get("current_exam_difficulty") != difficulty:

            questions_from_db = get_questions(topic, difficulty)

            if questions_from_db:
                st.success(f"🧪 {len(questions_from_db)} questions loaded.")

                # Shuffle the order of questions for the exam (only once when loaded)
                random.shuffle(questions_from_db)

                # Prepare exam questions with shuffled options and correct answer text
                exam_questions_data = []
                for q_db in questions_from_db:
                    q_id, q_topic, q_difficulty, q_text, opt1, opt2, opt3, opt4, correct_ans_text = q_db

                    options_with_status = [
                        (opt1, opt1 == correct_ans_text),
                        (opt2, opt2 == correct_ans_text),
                        (opt3, opt3 == correct_ans_text),
                        (opt4, opt4 == correct_ans_text),
                    ]

                    random.shuffle(options_with_status)

                    shuffled_options_texts = [opt[0] for opt in options_with_status]

                    exam_questions_data.append({
                        "id": q_id,
                        "question_text": q_text,
                        "shuffled_options": shuffled_options_texts,
                        "correct_answer_text": correct_ans_text 
                    })

                st.session_state.current_exam_questions = exam_questions_data
                st.session_state.current_exam_topic = topic
                st.session_state.current_exam_difficulty = difficulty
                st.session_state.exam_active = False # Ensure exam is not active initially
                st.session_state.user_answers = {} # Reset answers for new set of questions
                st.session_state.exam_submitted = False # New flag to control review display
            else:
                st.warning("⚠️ No questions found for selected topic and difficulty. Please generate some first.")
                st.session_state.current_exam_questions = [] # Clear if no questions found

        # Use the questions from session state for display
        exam_questions_data = st.session_state.get("current_exam_questions", [])

        if exam_questions_data and not st.session_state.get("exam_submitted", False): # Only show exam if not submitted
            # Timer setup - only show and manage if exam is active
            exam_duration = len(exam_questions_data) * 60  # 60 sec per question (adjust as needed)

            if "exam_start_time" not in st.session_state or not st.session_state.get("exam_active"):
                # Only show start button if exam is not active
                if st.button("Start Exam"):
                    st.session_state.exam_start_time = time.time()
                    st.session_state.exam_active = True
                    # Ensure user_answers are initialized correctly for the current set of questions
                    st.session_state.user_answers = {q_data["id"]: (None, q_data["correct_answer_text"]) for q_data in exam_questions_data}
                    st.rerun() # Rerun to display questions and timer

            elif st.session_state.get("exam_active"):
                time_left = exam_duration - int(time.time() - st.session_state.exam_start_time)
                if time_left <= 0:
                    st.warning("⏰ Time's up! Auto-submitting...")
                    st.session_state.exam_active = False
                    st.session_state.exam_submitted = True # Mark as submitted
                    time_left = 0 # Ensure time_left doesn't go negative for display
                    st.rerun() # Rerun to show results
                mins, secs = divmod(time_left, 60)
                st.info(f"⏱️ Time Remaining: {mins:02}:{secs:02}")

                # Display questions for the exam
                for q_data in exam_questions_data:
                    st.subheader(f"Q{q_data['id']}: {q_data['question_text']}")

                    radio_key = f"q_radio_{q_data['id']}_{st.session_state.exam_start_time}" # Add exam_start_time to key for uniqueness per exam instance

                    # Get the currently selected answer for this question from session_state
                    # st.session_state.user_answers stores (user_choice, correct_ans_text)
                    current_selected_option = st.session_state.user_answers.get(q_data['id'], (None, None))[0]

                    # Find the index of the currently selected option in the shuffled options for pre-selection
                    try:
                        index_of_selected = q_data['shuffled_options'].index(current_selected_option) if current_selected_option else None
                    except ValueError: # In case the option somehow isn't in the shuffled list (shouldn't happen if logic is correct)
                        index_of_selected = None 

                    user_choice = st.radio(
                        f"Choose your answer for Q{q_data['id']}:",
                        q_data["shuffled_options"],
                        key=radio_key,
                        index=index_of_selected # Set initial selected option
                    )

                    # Update user's answer in session state immediately on selection
                    # This line is crucial for persistence
                    if st.session_state.user_answers[q_data["id"]][0] != user_choice: # Only update if choice changed to avoid unnecessary reruns
                        st.session_state.user_answers[q_data["id"]] = (user_choice, q_data["correct_answer_text"])
                        st.rerun() # Rerun to reflect the selection across the app immediately (e.g., if other questions are shown)

                submit_button_pressed = st.button("Submit Exam")

                if submit_button_pressed or time_left == 0:
                    st.session_state.exam_active = False # Deactivate exam
                    st.session_state.exam_submitted = True # Mark as submitted

                    correct_count = 0
                    total_questions_attempted = len(st.session_state.user_answers)
                    for q_id, (user_ans, correct_ans_text) in st.session_state.user_answers.items():
                        if user_ans == correct_ans_text:
                            correct_count += 1

                    # Ensure user_id is available before recording
                    if st.session_state.user_id:
                        record_exam_result(
                            st.session_state.user_id,
                            topic, # Topic from the input field
                            difficulty, # Difficulty from the input field
                            correct_count,
                            total_questions_attempted
                        )
                        st.success("✅ Exam results recorded!")
                    else:
                        st.warning("Cannot record results: User not logged in.")

                    st.rerun() # Rerun to display results

            else: # Initial state, or after exam finished (before review is shown)
                if not st.session_state.get("current_exam_questions"):
                    st.warning("⚠️ No questions found for selected topic and difficulty. Please generate some first.")
                else:
                    st.info("Click 'Start Exam' to begin.")

        # --- Display Review Section AFTER submission ---
        if st.session_state.get("exam_submitted"):
            correct_count = 0
            total_questions_attempted = len(st.session_state.user_answers) # Use length of user_answers

            # Calculate score
            for q_id, (user_ans, correct_ans_text) in st.session_state.user_answers.items():
                if user_ans == correct_ans_text:
                    correct_count += 1

            st.success(f"🎯 You scored {correct_count} out of {total_questions_attempted}")

            st.subheader("Review your answers:")
            # Iterate through exam_questions_data (the original shuffled order) for consistent review display
            for q_data in exam_questions_data:
                q_id = q_data['id']
                # Fetch user's answer and correct answer from the session state
                user_ans_for_review, correct_ans_text_for_review = st.session_state.user_answers.get(q_id, (None, None))

                st.write(f"**Question {q_data['id']}:** {q_data['question_text']}")
                st.write(f"Your answer: **{user_ans_for_review if user_ans_for_review else 'No answer selected'}**")
                st.write(f"Correct answer: **{correct_ans_text_for_review}**")
                if user_ans_for_review == correct_ans_text_for_review:
                    st.write("Result: ✅ Correct")
                else:
                    st.write("Result: ❌ Incorrect")
                st.markdown("---")

            # Provide a button to clear session state and start fresh
            if st.button("Start New Exam"):
                st.session_state.clear() # Clears all session state variables
                st.rerun() # Rerun to go back to the initial state

    #--------------------------------------------------------------------------------------------------------------------------------------------------

    elif choice == "View Saved Questions":
        st.header("📄 All Saved Questions")

        # Filtering
        topic_filter = st.text_input("Filter by Topic (optional)", "")
        difficulty_filter = st.selectbox("Filter by Difficulty", ["", "easy", "medium", "hard"])

        # Fetch all or filtered questions
        questions = get_questions(topic_filter, difficulty_filter) if topic_filter or difficulty_filter else get_questions_all()

        # Pagination setup
        questions_per_page = 5
        if "page" not in st.session_state:
            st.session_state.page = 0

        total_questions = len(questions)
        start_idx = st.session_state.page * questions_per_page
        end_idx = start_idx + questions_per_page
        paginated_questions = questions[start_idx:end_idx]

        if paginated_questions:
            for i, q in enumerate(paginated_questions, start=start_idx + 1):
                st.markdown(f"### Q{i}: {q[3]}") # q[3] is the question text
                st.write(f"**Topic:** {q[1]}  |  **Difficulty:** {q[2]}")

                options = list(q[4:8]) # q[4] to q[7] are options
                answer = q[8] # q[8] is the correct answer text

                # Display options
                for opt in options:
                    st.write(f"- {opt}")
                st.markdown(f"✅ **Answer:** {answer}")

                # Expandable Edit Section
                with st.expander("✏️ Edit this question"):
                    new_q = st.text_input("Edit Question", q[3], key=f"edit_q_text_{q[0]}")
                    new_opts = [st.text_input(f"Option {chr(65+j)}", options[j], key=f"edit_opt_{j}_{q[0]}") for j in range(4)]

                    # Safely find the index of the correct answer for the selectbox
                    try:
                        answer_index = new_opts.index(answer)
                    except ValueError:
                        # Fallback if the original answer text is not found in the new_opts
                        # (e.g., if user changed the correct answer text)
                        answer_index = 0

                    new_ans = st.selectbox("Correct Answer", new_opts, index=answer_index, key=f"edit_ans_select_{q[0]}")

                    if st.button("Save Changes", key=f"save_{q[0]}"):
                        update_question(q[0], new_q, new_opts, new_ans)
                        st.success("✅ Question updated. Refreshing...")
                        st.rerun() # <--- CHANGE HERE

                # Delete button
                if st.button("🗑️ Delete", key=f"del_{q[0]}"):
                    delete_question_by_id(q[0])
                    st.warning("⚠️ Question deleted. Refreshing...")
                    st.rerun() # <--- CHANGE HERE

                st.markdown("---")
        else:
            st.info("No questions found based on current filters.")

        # Pagination controls
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⬅️ Previous", disabled=st.session_state.page <= 0, key="prev_page_btn"):
                st.session_state.page -= 1
                st.rerun()
        with col2:
            num_pages = ((total_questions - 1) // questions_per_page) + 1 if total_questions > 0 else 1
            st.write(f"Page {st.session_state.page + 1} of {num_pages}")
        with col3:
            if st.button("Next ➡️", disabled=end_idx >= total_questions, key="next_page_btn"):
                st.session_state.page += 1
                st.rerun()

    elif choice == "Exam History":
        st.header("📈 Your Exam History")
        if st.session_state.user_id:
            user_results = get_user_exam_results(st.session_state.user_id)
            if user_results:
                st.write("Here are your past exam results:")
                for result in user_results:
                    exam_date, topic, difficulty, score, total_questions = result
                    st.markdown(f"**Date:** {exam_date}")
                    st.markdown(f"**Topic:** {topic} | **Difficulty:** {difficulty}")
                    st.markdown(f"**Score:** {score} / {total_questions}")
                    if total_questions > 0:
                        percentage = (score / total_questions) * 100
                        st.markdown(f"**Percentage:** {percentage:.2f}%")
                    st.markdown("---")
            else:
                st.info("You haven't taken any exams yet. Go to 'Take Exam' to start!")
        else:
            st.warning("Please login to view your exam history.")

else:
    st.info("Please login or register to access the exam portal features.")
    st.markdown("---")
    st.markdown("You can generate and manage questions, take exams, and review your performance.")
