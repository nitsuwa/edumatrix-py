import numpy as np
from scipy import stats

class AnalyticsEngine:
    def __init__(self, weights):
        self.w_quiz = weights['quiz']
        self.w_mid = weights['midterm']
        self.w_final = weights['final']

    def calculate_weighted_gpa(self, q, m, f):
        grades = np.array([q, m, f])
        weights = np.array([self.w_quiz, self.w_mid, self.w_final])
        return np.dot(grades, weights)

    def get_class_performance(self, all_grades):
        if not all_grades: return 0, 0
        avg_grade = np.mean(all_grades)
        passing = sum(1 for g in all_grades if g >= 75)
        pass_rate = (passing / len(all_grades)) * 100
        return round(avg_grade, 2), round(pass_rate, 1)

    def predict_performance(self, attendance_array, grades_array):
        if len(attendance_array) < 2:
            return None
        slope, intercept, r_value, p_value, std_err = stats.linregress(attendance_array, grades_array)
        return {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_value**2,
            "correlation": r_value
        }

    def generate_insight_text(self, r_value):
        if r_value > 0.7:
            return "Analysis: Strong positive correlation.\nHigh attendance consistently leads to better grades."
        elif r_value > 0.3:
            return "Analysis: Moderate correlation.\nAttendance helps, but other factors (aptitude) matter."
        else:
            return "Analysis: Weak correlation.\nGrades are inconsistent regardless of attendance."