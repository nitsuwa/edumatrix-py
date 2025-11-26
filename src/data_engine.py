import sqlite3
import os


class DataEngine:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                course TEXT,
                year_level INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_foreign_id TEXT,
                attendance_rate REAL,
                quiz_score REAL,
                midterm_score REAL,
                final_score REAL,
                FOREIGN KEY(student_foreign_id) REFERENCES students(student_id)
            )
        """)
        conn.commit()
        conn.close()

    def add_student_record(self, s_id, name, course, year, attendance, q, m, f):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO students (student_id, full_name, course, year_level) VALUES (?, ?, ?, ?)",
                           (s_id, name, course, year))
            cursor.execute(
                "INSERT INTO grades (student_foreign_id, attendance_rate, quiz_score, midterm_score, final_score) VALUES (?, ?, ?, ?, ?)",
                (s_id, attendance, q, m, f))
            conn.commit()
            return True, "Record Created Successfully"
        except sqlite3.IntegrityError:
            return False, "Error: Student ID already exists."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    # NEW: UPDATE FUNCTION
    def update_student_record(self, s_id, name, attendance, q, m, f):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Update Profile
            cursor.execute("UPDATE students SET full_name=? WHERE student_id=?", (name, s_id))
            # Update Grades
            cursor.execute(
                "UPDATE grades SET attendance_rate=?, quiz_score=?, midterm_score=?, final_score=? WHERE student_foreign_id=?",
                (attendance, q, m, f, s_id))
            conn.commit()
            return True, "Record Updated Successfully"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def fetch_analytics_data(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = """
            SELECT s.full_name, s.student_id, g.attendance_rate, g.quiz_score, g.midterm_score, g.final_score
            FROM students s
            JOIN grades g ON s.student_id = g.student_foreign_id
        """
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return data

    def search_students(self, query_text):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = """
            SELECT s.full_name, s.student_id, g.attendance_rate, g.quiz_score, g.midterm_score, g.final_score
            FROM students s
            JOIN grades g ON s.student_id = g.student_foreign_id
            WHERE s.full_name LIKE ? OR s.student_id LIKE ?
        """
        cursor.execute(query, (f'%{query_text}%', f'%{query_text}%'))
        data = cursor.fetchall()
        conn.close()
        return data

    def get_summary_stats(self):
        data = self.fetch_analytics_data()
        total_students = len(data)
        if total_students == 0:
            return {"total": 0, "avg_attendance": 0}

        total_att = sum([row[2] for row in data])
        return {
            "total": total_students,
            "avg_attendance": round(total_att / total_students, 2)
        }

    def delete_record(self, s_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM grades WHERE student_foreign_id=?", (s_id,))
        cursor.execute("DELETE FROM students WHERE student_id=?", (s_id,))
        conn.commit()
        conn.close()