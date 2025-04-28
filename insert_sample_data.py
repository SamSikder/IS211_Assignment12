import sqlite3

conn = sqlite3.connect('hw13.db')
c = conn.cursor()

# Insert student John Smith
c.execute("INSERT INTO students (first_name, last_name) VALUES (?, ?)", ('John', 'Smith'))

# Insert quiz Python Basics
c.execute("INSERT INTO quizzes (subject, num_questions, quiz_date) VALUES (?, ?, ?)", ('Python Basics', 5, '2015-02-05'))

# Insert John's result (assume student ID 1, quiz ID 1)
c.execute("INSERT INTO results (student_id, quiz_id, score) VALUES (?, ?, ?)", (1, 1, 85))

conn.commit()
conn.close()

print("Sample data inserted successfully!")
