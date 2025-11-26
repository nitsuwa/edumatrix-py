import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from PIL import Image
import re
import platform
import os
import csv
import json
import sys  # ADDED: Needed for the restart command
from datetime import datetime

# Set Theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class ModernUI(ctk.CTk):
    def __init__(self, auth_callback, db_engine, math_engine, icon_path):
        super().__init__()
        self.auth_callback = auth_callback
        self.db = db_engine
        self.math = math_engine
        self.icon_path = icon_path

        self.current_stats = None

        self.title("EduMatrix Enterprise Suite | PLV Edition")

        # --- CENTER WINDOW LOGIC ---
        window_width = 1280
        window_height = 850
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))

        self.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        try:
            image_file = Image.open(icon_path)
            self.logo_image = ctk.CTkImage(light_image=image_file, dark_image=image_file, size=(90, 90))
            self.iconbitmap(icon_path)
        except Exception as e:
            self.logo_image = None

        self.show_login()

    def on_close(self):
        if messagebox.askyesno("Exit System", "Are you sure you want to close the application?"):
            self.destroy()

    def play_sound(self, type="notify"):
        system_os = platform.system()
        try:
            if system_os == "Windows":
                import winsound
                if type == "error":
                    winsound.MessageBeep(winsound.MB_ICONHAND)
                elif type == "success":
                    winsound.MessageBeep(winsound.MB_OK)
                else:
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
            elif system_os == "Darwin":
                sound = "Basso" if type == "error" else "Glass"
                os.system(f"afplay /System/Library/Sounds/{sound}.aiff &")
        except:
            pass

    # --- LOGIN SCREEN ---
    def show_login(self):
        for widget in self.winfo_children(): widget.destroy()
        self.bind('<Return>', lambda event: self.verify_login())

        self.login_bg = ctk.CTkFrame(self, corner_radius=0, fg_color=("#ecf0f1", "#1a1a1a"))
        self.login_bg.pack(fill="both", expand=True)

        self.login_frame = ctk.CTkFrame(self.login_bg, corner_radius=20, width=480, height=680,
                                        fg_color=("white", "#2b2b2b"))
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        content_box = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        content_box.pack(fill="both", expand=True, padx=40, pady=40)

        if self.logo_image:
            ctk.CTkLabel(content_box, text="", image=self.logo_image).pack(pady=(10, 15))

        ctk.CTkLabel(content_box, text="EDUMATRIX", font=("Roboto", 34, "bold"), text_color=("black", "white")).pack(
            pady=(0, 5))
        ctk.CTkLabel(content_box, text="Academic Intelligence Platform", font=("Roboto", 14), text_color="gray").pack(
            pady=(0, 40))

        ctk.CTkLabel(content_box, text="Username", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w",
                                                                                                       padx=5)
        self.user_entry = ctk.CTkEntry(content_box, width=340, height=50, font=("Arial", 14))
        self.user_entry.pack(pady=(5, 20))

        ctk.CTkLabel(content_box, text="Password", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w",
                                                                                                       padx=5)
        self.pass_entry = ctk.CTkEntry(content_box, show="•", width=340, height=50, font=("Arial", 14))
        self.pass_entry.pack(pady=(5, 30))

        ctk.CTkButton(content_box, text="SECURE ACCESS", command=self.verify_login, width=340, height=55,
                      font=("Roboto", 15, "bold"), fg_color="#003366", hover_color="#004080").pack(pady=10)

        ctk.CTkLabel(content_box, text="v2.5.0 Enterprise Edition", font=("Arial", 10), text_color="gray").pack(
            side="bottom", pady=10)
        self.user_entry.focus()

    def verify_login(self):
        u = self.user_entry.get().strip()
        p = self.pass_entry.get().strip()

        if not u or not p:
            self.play_sound("error")
            self.user_entry.configure(border_color="#c0392b")
            self.pass_entry.configure(border_color="#c0392b")
            messagebox.showwarning("Authentication", "Please enter both Username and Password.")
            return

        if self.auth_callback(u, p):
            self.play_sound("success")
            self.unbind('<Return>')
            self.login_bg.destroy()
            self.build_dashboard()
        else:
            self.play_sound("error")
            self.pass_entry.delete(0, 'end')
            messagebox.showerror("Access Denied", "Invalid Credentials.\nContact System Administrator.")

    def logout(self):
        if messagebox.askyesno("Logout", "End current session?"):
            self.sidebar.destroy()
            self.content_area.destroy()
            self.show_login()

    # --- DASHBOARD ARCHITECTURE ---
    def build_dashboard(self):
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=("#0f172a", "#0f172a"))
        self.sidebar.pack(side="left", fill="y")

        if self.logo_image:
            ctk.CTkLabel(self.sidebar, text="", image=self.logo_image).pack(pady=(40, 10))

        ctk.CTkLabel(self.sidebar, text="EDUMATRIX", font=("Roboto", 22, "bold"), text_color="white").pack(pady=(0, 5))
        ctk.CTkLabel(self.sidebar, text="Administrator Panel", font=("Arial", 12), text_color="#94a3b8").pack(
            pady=(0, 40))

        self.create_nav_btn("Dashboard", "home", "🏠")
        self.create_nav_btn("Student Records", "records", "👥")
        self.create_nav_btn("Intelligence Hub", "analytics", "📈")
        self.create_nav_btn("Honors & Intervention", "honors", "🏅")
        self.create_nav_btn("System Settings", "settings", "⚙️")
        self.create_nav_btn("User Manual", "about", "ℹ️")

        ctk.CTkButton(self.sidebar, text="🚪 LOGOUT", command=self.logout,
                      fg_color="#c0392b", hover_color="#e74c3c", height=45, font=("Arial", 12, "bold")).pack(
            side="bottom", pady=30, padx=20, fill="x")

        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color=("#f1f5f9", "#121212"))
        self.content_area.pack(side="right", fill="both", expand=True)

        self.frames = {}
        self.frames["home"] = self.create_home_frame()
        self.frames["records"] = self.create_records_frame()
        self.frames["analytics"] = self.create_analytics_frame()
        self.frames["honors"] = self.create_honors_frame()
        self.frames["settings"] = self.create_settings_frame()
        self.frames["about"] = self.create_about_frame()

        self.switch_tab("home")

    def create_nav_btn(self, text, name, icon):
        btn = ctk.CTkButton(self.sidebar, text=f"  {icon}    {text}", command=lambda: self.switch_tab(name),
                            fg_color="transparent", hover_color="#1e293b",
                            anchor="w", height=50, font=("Roboto", 15), text_color="#e2e8f0")
        btn.pack(fill="x", padx=10, pady=5)

    def switch_tab(self, name):
        for frame in self.frames.values(): frame.pack_forget()
        self.frames[name].pack(fill="both", expand=True, padx=30, pady=30)
        if name == "home": self.update_home_stats()
        if name == "honors": self.refresh_honors()

    # --- TAB 1: HOME ---
    def create_home_frame(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        ctk.CTkLabel(frame, text="System Overview", font=("Roboto", 32, "bold"), text_color=("black", "white")).pack(
            anchor="w", pady=(0, 20))

        self.stats_grid = ctk.CTkFrame(frame, fg_color="transparent")
        self.stats_grid.pack(fill="x", pady=10)

        self.card_total = self.create_stat_card(self.stats_grid, "Total Students", "0", "#2980b9")
        self.card_avg = self.create_stat_card(self.stats_grid, "Class GPA", "0.00", "#27ae60")
        self.card_pass = self.create_stat_card(self.stats_grid, "Pass Rate", "0%", "#8e44ad")

        ctk.CTkLabel(frame, text="Quick Actions", font=("Roboto", 22, "bold"), text_color=("black", "white")).pack(
            anchor="w", pady=(40, 10))

        actions = ctk.CTkFrame(frame, fg_color=("white", "#1e1e1e"), corner_radius=15)
        actions.pack(fill="x", ipady=30)

        ctk.CTkButton(actions, text="+ Add New Student", command=lambda: self.switch_tab("records"), width=250,
                      height=60,
                      font=("Arial", 14, "bold"), fg_color="#003366", hover_color="#004080").pack(side="left", padx=50,
                                                                                                  expand=True)
        ctk.CTkButton(actions, text="⚡ Run Regression AI", command=lambda: self.switch_tab("analytics"), width=250,
                      height=60,
                      fg_color="#e67e22", hover_color="#d35400", font=("Arial", 14, "bold")).pack(side="left", padx=50,
                                                                                                  expand=True)
        return frame

    def create_stat_card(self, parent, title, value, color):
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=15)
        card.pack(side="left", padx=10, expand=True, fill="x")
        ctk.CTkLabel(card, text=title, font=("Arial", 16), text_color="white").pack(pady=(25, 5))
        ctk.CTkLabel(card, text=value, font=("Arial", 48, "bold"), text_color="white").pack(pady=(0, 25))
        return card

    def update_home_stats(self):
        for widget in self.stats_grid.winfo_children(): widget.destroy()
        data = self.db.fetch_analytics_data()
        grades = [self.math.calculate_weighted_gpa(row[3], row[4], row[5]) for row in data]
        summary = self.db.get_summary_stats()
        avg_gpa, pass_rate = self.math.get_class_performance(grades)
        self.create_stat_card(self.stats_grid, "Total Students", str(summary['total']), "#2980b9")
        self.create_stat_card(self.stats_grid, "Class Average (GPA)", f"{avg_gpa}", "#27ae60")
        self.create_stat_card(self.stats_grid, "Pass Rate", f"{pass_rate}%", "#8e44ad")

    # --- TAB 2: RECORDS ---
    def create_records_frame(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")

        head = ctk.CTkFrame(frame, fg_color="transparent")
        head.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(head, text="Student Database", font=("Roboto", 28, "bold"), text_color=("black", "white")).pack(
            side="left")

        ctk.CTkLabel(head, text="Search Records:", font=("Arial", 14, "bold"), text_color=("gray50", "gray80")).pack(
            side="left", padx=(40, 10))

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda name, index, mode, sv=self.search_var: self.run_search())
        search_entry = ctk.CTkEntry(head, placeholder_text="Enter Name or ID...", width=300, height=40,
                                    textvariable=self.search_var)
        search_entry.pack(side="left")
        search_entry.bind('<Return>', lambda event: self.run_search())

        input_panel = ctk.CTkFrame(frame, fg_color=("white", "#1e1e1e"), corner_radius=15)
        input_panel.pack(fill="x", pady=10, ipady=10)
        ctk.CTkLabel(input_panel, text="Add / Edit Record", font=("Roboto", 18, "bold"),
                     text_color=("black", "white")).pack(anchor="w", padx=20, pady=10)

        fields = ctk.CTkFrame(input_panel, fg_color="transparent")
        fields.pack(fill="x", padx=10)

        r1 = ctk.CTkFrame(fields, fg_color="transparent")
        r1.pack(fill="x", pady=5)
        self.ent_id = self.create_labeled_entry(r1, "Student ID", "Format: 23-XXXX", "left")
        self.ent_name = self.create_labeled_entry(r1, "Full Name", "Format: Last, First", "left")
        self.ent_att = self.create_labeled_entry(r1, "Attendance Rate", "0-100 (No % symbol)", "left")

        r2 = ctk.CTkFrame(fields, fg_color="transparent")
        r2.pack(fill="x", pady=5)

        q_w = int(self.math.w_quiz * 100)
        m_w = int(self.math.w_mid * 100)
        f_w = int(self.math.w_final * 100)

        self.ent_q = self.create_labeled_entry(r2, "Quiz Score", f"Weight: {q_w}% (0-100)", "left")
        self.ent_m = self.create_labeled_entry(r2, "Midterm Score", f"Weight: {m_w}% (0-100)", "left")
        self.ent_f = self.create_labeled_entry(r2, "Finals Score", f"Weight: {f_w}% (0-100)", "left")

        ctk.CTkButton(input_panel, text="💾 SAVE RECORD", fg_color="#27ae60", hover_color="#2ecc71", width=200,
                      height=45,
                      font=("Arial", 14, "bold"), command=self.save_student).pack(pady=20)

        table_bg = ctk.CTkFrame(frame, fg_color=("white", "#1e1e1e"), corner_radius=10)
        table_bg.pack(fill="both", expand=True, pady=10)

        table_frame = tk.Frame(table_bg)
        table_frame.pack(fill="both", expand=True, padx=15, pady=15)

        cols = ("Name", "ID", "Attendance", "Weighted GPA")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=8)
        for col in cols: self.tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c, False))
        self.tree.pack(fill="both", expand=True)

        btn_box = ctk.CTkFrame(frame, fg_color="transparent")
        btn_box.pack(fill="x", pady=5)

        ctk.CTkButton(btn_box, text="🔄 Refresh List", command=self.refresh_table, fg_color="gray", height=35).pack(
            side="left", expand=True, padx=5)
        ctk.CTkButton(btn_box, text="✏️ EDIT SELECTED", command=self.edit_student, fg_color="#f39c12",
                      hover_color="#e67e22", height=35).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_box, text="🗑️ DELETE SELECTED", command=self.delete_student, fg_color="#c0392b",
                      hover_color="#e74c3c", height=35).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_box, text="📄 EXPORT CSV", command=self.export_csv, fg_color="#2980b9", hover_color="#3498db",
                      height=35).pack(side="right", expand=True, padx=5)

        return frame

    def create_labeled_entry(self, parent, label_text, help_text, side):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side=side, expand=True, fill="x", padx=10)
        ctk.CTkLabel(container, text=label_text, font=("Arial", 13, "bold"), text_color=("black", "white")).pack(
            anchor="w")
        ent = ctk.CTkEntry(container, height=35)
        ent.pack(anchor="w", pady=(5, 0), fill="x")
        ctk.CTkLabel(container, text=help_text, font=("Arial", 11), text_color="gray").pack(anchor="w")
        return ent

    def save_student(self):
        s_id = self.ent_id.get().strip()
        name = self.ent_name.get().strip()
        if not s_id or not name:
            self.play_sound("error")
            messagebox.showwarning("Input Error", "Name and ID are required.")
            return
        if not re.match(r"^\d{2}-\d{4}$", s_id):
            self.play_sound("error")
            messagebox.showerror("Validation Error", "Student ID must follow format: XX-XXXX\nExample: 23-1024")
            return
        try:
            att = float(self.ent_att.get())
            q, m, f = float(self.ent_q.get()), float(self.ent_m.get()), float(self.ent_f.get())
            if not (0 <= q <= 100 and 0 <= m <= 100 and 0 <= f <= 100 and 0 <= att <= 100): raise ValueError

            success, msg = self.db.add_student_record(s_id, name, "BSIT", 3, att, q, m, f)
            if success:
                self.play_sound("success")
                self.refresh_table()
                self.ent_id.delete(0, 'end')
                self.ent_name.delete(0, 'end')
                self.ent_att.delete(0, 'end')
                self.ent_q.delete(0, 'end')
                self.ent_m.delete(0, 'end')
                self.ent_f.delete(0, 'end')
                messagebox.showinfo("Success", msg)
            else:
                self.play_sound("error")
                messagebox.showerror("Database Error", msg)
        except:
            self.play_sound("error")
            messagebox.showerror("Input Error", "Values must be numbers 0-100.")

    def edit_student(self):
        selected = self.tree.selection()
        if not selected:
            self.play_sound("error")
            messagebox.showwarning("Selection Error", "Please select a student record to edit.")
            return

        item = self.tree.item(selected)
        s_id = item['values'][1]

        raw_data = None
        all_students = self.db.fetch_analytics_data()
        for row in all_students:
            if row[1] == s_id:
                raw_data = row
                break
        if not raw_data: return

        edit_window = ctk.CTkToplevel(self)
        edit_window.title(f"Edit Record: {s_id}")

        w = 500
        h = 600
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        edit_window.geometry(f"{w}x{h}+{x}+{y}")
        edit_window.grab_set()

        ctk.CTkLabel(edit_window, text="Update Student Details", font=("Roboto", 20, "bold")).pack(pady=20)

        f_frame = ctk.CTkFrame(edit_window, fg_color="transparent")
        f_frame.pack(fill="x", padx=20)

        q_w = int(self.math.w_quiz * 100)
        m_w = int(self.math.w_mid * 100)
        f_w = int(self.math.w_final * 100)

        ctk.CTkLabel(f_frame, text="Full Name", font=("Arial", 12, "bold")).pack(anchor="w")
        e_name = ctk.CTkEntry(f_frame)
        e_name.pack(fill="x", pady=(0, 2))
        ctk.CTkLabel(f_frame, text="Format: Last, First", font=("Arial", 10), text_color="gray").pack(anchor="w",
                                                                                                      pady=(0, 10))
        e_name.insert(0, raw_data[0])

        ctk.CTkLabel(f_frame, text="Attendance %", font=("Arial", 12, "bold")).pack(anchor="w")
        e_att = ctk.CTkEntry(f_frame)
        e_att.pack(fill="x", pady=(0, 2))
        ctk.CTkLabel(f_frame, text="0-100 (No % symbol)", font=("Arial", 10), text_color="gray").pack(anchor="w",
                                                                                                      pady=(0, 10))
        e_att.insert(0, str(raw_data[2]))

        ctk.CTkLabel(f_frame, text="Quiz Score", font=("Arial", 12, "bold")).pack(anchor="w")
        e_q = ctk.CTkEntry(f_frame)
        e_q.pack(fill="x", pady=(0, 2))
        ctk.CTkLabel(f_frame, text=f"Weight: {q_w}% (0-100)", font=("Arial", 10), text_color="gray").pack(anchor="w",
                                                                                                          pady=(0, 10))
        e_q.insert(0, str(raw_data[3]))

        ctk.CTkLabel(f_frame, text="Midterm Score", font=("Arial", 12, "bold")).pack(anchor="w")
        e_m = ctk.CTkEntry(f_frame)
        e_m.pack(fill="x", pady=(0, 2))
        ctk.CTkLabel(f_frame, text=f"Weight: {m_w}% (0-100)", font=("Arial", 10), text_color="gray").pack(anchor="w",
                                                                                                          pady=(0, 10))
        e_m.insert(0, str(raw_data[4]))

        ctk.CTkLabel(f_frame, text="Finals Score", font=("Arial", 12, "bold")).pack(anchor="w")
        e_f = ctk.CTkEntry(f_frame)
        e_f.pack(fill="x", pady=(0, 2))
        ctk.CTkLabel(f_frame, text=f"Weight: {f_w}% (0-100)", font=("Arial", 10), text_color="gray").pack(anchor="w",
                                                                                                          pady=(0, 20))
        e_f.insert(0, str(raw_data[5]))

        def confirm_update():
            try:
                att = float(e_att.get())
                q, m, f = float(e_q.get()), float(e_m.get()), float(e_f.get())
                if not (0 <= q <= 100 and 0 <= m <= 100 and 0 <= f <= 100 and 0 <= att <= 100): raise ValueError

                success, msg = self.db.update_student_record(s_id, e_name.get(), att, q, m, f)
                if success:
                    self.play_sound("success")
                    self.refresh_table()
                    edit_window.destroy()
                    messagebox.showinfo("Updated", "Record updated successfully.")
                else:
                    self.play_sound("error")
                    messagebox.showerror("Error", msg)
            except:
                self.play_sound("error")
                messagebox.showerror("Error", "Invalid inputs. Use numbers 0-100.")

        ctk.CTkButton(edit_window, text="CONFIRM UPDATE", command=confirm_update, fg_color="#2980b9", height=45).pack(
            pady=10, padx=20, fill="x")

    def refresh_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        data = self.db.fetch_analytics_data()
        for row in data:
            gpa = self.math.calculate_weighted_gpa(row[3], row[4], row[5])
            self.tree.insert("", "end", values=(row[0], row[1], f"{row[2]}%", f"{gpa:.2f}"))

    def run_search(self):
        query = self.search_var.get()
        data = self.db.search_students(query)
        for i in self.tree.get_children(): self.tree.delete(i)
        for row in data:
            gpa = self.math.calculate_weighted_gpa(row[3], row[4], row[5])
            self.tree.insert("", "end", values=(row[0], row[1], f"{row[2]}%", f"{gpa:.2f}"))

    def sort_treeview(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            l.sort(key=lambda t: float(t[0].replace('%', '')), reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l): self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))

    def delete_student(self):
        selected = self.tree.selection()
        if not selected:
            self.play_sound("error")
            messagebox.showwarning("Selection Error", "Please select a record.")
            return
        if messagebox.askyesno("Confirm Delete", "This action cannot be undone."):
            try:
                for item in selected:
                    self.db.delete_record(self.tree.item(item, 'values')[1])
                self.play_sound("success")
                self.refresh_table()
            except Exception as e:
                self.play_sound("error")
                messagebox.showerror("Error", str(e))

    def export_csv(self):
        data = self.db.fetch_analytics_data()
        if not data:
            messagebox.showwarning("Export Failed", "No data to export.")
            return
        try:
            export_dir = "exports"
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            filename = f"{export_dir}/Student_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Full Name", "Student ID", "Attendance %", "Quiz", "Midterm", "Finals"])
                writer.writerows(data)
            self.play_sound("success")
            messagebox.showinfo("Export Success", f"Saved to:\n{filename}")
            os.startfile(export_dir)
        except Exception as e:
            self.play_sound("error")
            messagebox.showerror("Export Error", str(e))

    # --- TAB 3: ANALYTICS ---
    def create_analytics_frame(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        ctk.CTkLabel(frame, text="Intelligence Hub", font=("Roboto", 28, "bold"), text_color=("black", "white")).pack(
            anchor="w", pady=(0, 10))

        info_box = ctk.CTkFrame(frame, fg_color=("white", "#1e1e1e"), corner_radius=10)
        info_box.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(info_box, text="💡 How to use AI Analytics:", font=("Arial", 14, "bold"),
                     text_color=("black", "white")).pack(anchor="w", padx=20, pady=(10, 5))
        ctk.CTkLabel(info_box,
                     text="• Regression Model: Predicts GPA based on Attendance Rate.\n• Class Distribution: Visualizes the pass/fail ratio.",
                     font=("Arial", 12), justify="left", text_color="gray").pack(anchor="w", padx=20, pady=(0, 10))

        tabs = ctk.CTkTabview(frame, width=500, height=450, text_color=("black", "white"))
        tabs.pack(fill="both", expand=True)
        tabs.add("Regression Model")
        tabs.add("Class Distribution")

        # REGRESSION TAB
        reg_tab = tabs.tab("Regression Model")
        self.reg_canvas = ctk.CTkFrame(reg_tab, fg_color="transparent")
        self.reg_canvas.pack(fill="both", expand=True, padx=10, pady=10)

        ctrl_frame = ctk.CTkFrame(reg_tab, fg_color="transparent")
        ctrl_frame.pack(fill="x", pady=10)
        ctk.CTkButton(ctrl_frame, text="⚡ GENERATE MODEL", command=self.run_regression, width=180,
                      fg_color="#002366").pack(side="left", padx=20)

        # Predictor
        pred_box = ctk.CTkFrame(ctrl_frame, fg_color=("white", "#2b2b2b"), corner_radius=8)
        pred_box.pack(side="right", padx=20)
        ctk.CTkLabel(pred_box, text="Predictor:", font=("Arial", 12, "bold")).pack(side="left", padx=(10, 5))
        self.pred_entry = ctk.CTkEntry(pred_box, placeholder_text="Attend %", width=80)
        self.pred_entry.pack(side="left", padx=5)
        ctk.CTkButton(pred_box, text="Calc", width=60, command=self.calculate_prediction).pack(side="left", padx=5)
        self.pred_result = ctk.CTkLabel(pred_box, text="--", font=("Arial", 14, "bold"), text_color="#27ae60")
        self.pred_result.pack(side="left", padx=10)

        # FIXED: Added Helper Text below Predictor
        ctk.CTkLabel(ctrl_frame, text="(Enter Attendance % to forecast grade)", font=("Arial", 10),
                     text_color="gray").pack(side="right", padx=20)

        self.insight_label = ctk.CTkLabel(reg_tab, text="⚠ Waiting for command...", text_color="#f39c12",
                                          font=("Arial", 14, "bold"))
        self.insight_label.pack(pady=5)

        # DISTRIBUTION TAB
        pie_tab = tabs.tab("Class Distribution")
        self.pie_canvas = ctk.CTkFrame(pie_tab, fg_color="transparent")
        self.pie_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkButton(pie_tab, text="🔄 ANALYZE DISTRIBUTION", command=self.run_pie_chart, width=200,
                      fg_color="#002366").pack(pady=10)

        return frame

    def run_regression(self):
        data = self.db.fetch_analytics_data()
        if len(data) < 2:
            messagebox.showwarning("Insufficient Data", "Need at least 2 students.")
            return

        attendance = [row[2] for row in data]
        grades = [self.math.calculate_weighted_gpa(row[3], row[4], row[5]) for row in data]

        try:
            self.current_stats = self.math.predict_performance(attendance, grades)
            stats = self.current_stats

            for w in self.reg_canvas.winfo_children(): w.destroy()

            bg_color = "#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#f0f0f0"
            text_color = "white" if ctk.get_appearance_mode() == "Dark" else "black"

            fig, ax = plt.subplots(figsize=(5, 3), facecolor=bg_color)
            ax.set_facecolor(bg_color)
            ax.scatter(attendance, grades, color="#00b894", label="Student Data")
            line = [stats['slope'] * x + stats['intercept'] for x in attendance]
            ax.plot(attendance, line, color="#e17055", linewidth=2, label="Trend Line")

            ax.tick_params(axis='x', colors=text_color)
            ax.tick_params(axis='y', colors=text_color)
            ax.set_xlabel("Attendance (%)", color=text_color)
            ax.set_ylabel("Weighted GPA", color=text_color)
            ax.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.5)
            ax.legend()

            canvas = FigureCanvasTkAgg(fig, master=self.reg_canvas)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            self.insight_label.configure(text=self.math.generate_insight_text(stats['correlation']),
                                         text_color=text_color)

        except ValueError:
            messagebox.showwarning("Data Error",
                                   "Cannot predict trend: All students have the same Attendance rate.\nAdd varied data points.")

    def calculate_prediction(self):
        if not self.current_stats:
            messagebox.showwarning("AI Error", "Click 'Generate Model' first.")
            return
        try:
            val = float(self.pred_entry.get())
            if not (0 <= val <= 100): raise ValueError
            res = (self.current_stats['slope'] * val) + self.current_stats['intercept']
            self.pred_result.configure(text=f"{max(0, min(100, res)):.2f}")
        except:
            messagebox.showerror("Input Error", "Enter 0-100.")

    def run_pie_chart(self):
        data = self.db.fetch_analytics_data()
        if len(data) == 0:
            messagebox.showwarning("No Data", "Add records first.")
            return

        grades = [self.math.calculate_weighted_gpa(row[3], row[4], row[5]) for row in data]
        passing = sum(1 for g in grades if g >= 75)
        failing = len(grades) - passing

        for w in self.pie_canvas.winfo_children(): w.destroy()

        bg_color = "#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#f0f0f0"
        text_color = "white" if ctk.get_appearance_mode() == "Dark" else "black"

        fig, ax = plt.subplots(figsize=(5, 3), facecolor=bg_color)
        if passing == 0 and failing == 0:
            messagebox.showinfo("Data", "No grades available.")
            return

        ax.pie([passing, failing], labels=['Passing', 'Fail / At Risk'], autopct='%1.1f%%',
               colors=['#00b894', '#d63031'], textprops={'color': text_color})

        canvas = FigureCanvasTkAgg(fig, master=self.pie_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # --- TAB 4: HONORS & INTERVENTION ---
    def create_honors_frame(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        ctk.CTkLabel(frame, text="Honors & Intervention", font=("Roboto", 28, "bold"),
                     text_color=("black", "white")).pack(anchor="w", pady=(0, 10))

        container = ctk.CTkFrame(frame, fg_color="transparent")
        container.pack(fill="both", expand=True)

        left_frame = ctk.CTkFrame(container, fg_color=("white", "#1e1e1e"), corner_radius=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)
        ctk.CTkLabel(left_frame, text="🏆 Dean's List (GPA > 90)", font=("Arial", 16, "bold"),
                     text_color="#f1c40f").pack(pady=10)

        self.tree_honors = ttk.Treeview(left_frame, columns=("Name", "GPA"), show="headings", height=15)
        self.tree_honors.heading("Name", text="Student Name")
        self.tree_honors.heading("GPA", text="GPA")
        self.tree_honors.column("GPA", width=50, anchor="center")
        self.tree_honors.pack(fill="both", expand=True, padx=10, pady=10)

        right_frame = ctk.CTkFrame(container, fg_color=("white", "#1e1e1e"), corner_radius=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=10)
        ctk.CTkLabel(right_frame, text="⚠ At-Risk Students", font=("Arial", 16, "bold"), text_color="#e74c3c").pack(
            pady=10)

        self.tree_risk = ttk.Treeview(right_frame, columns=("Name", "Issue"), show="headings", height=15)
        self.tree_risk.heading("Name", text="Student Name")
        self.tree_risk.heading("Issue", text="Risk Factor")
        self.tree_risk.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkButton(frame, text="🔄 REFRESH LISTS", command=self.refresh_honors, fg_color="#002366").pack(pady=10)
        return frame

    def refresh_honors(self):
        for i in self.tree_honors.get_children(): self.tree_honors.delete(i)
        for i in self.tree_risk.get_children(): self.tree_risk.delete(i)

        data = self.db.fetch_analytics_data()
        if not data: return

        for row in data:
            name = row[0]
            attendance = row[2]
            gpa = self.math.calculate_weighted_gpa(row[3], row[4], row[5])

            if gpa >= 90:
                self.tree_honors.insert("", "end", values=(name, f"{gpa:.2f}"))

            risk_reasons = []
            if attendance < 80: risk_reasons.append("Low Attendance")
            if gpa < 75: risk_reasons.append("Failing Grades")

            if risk_reasons:
                self.tree_risk.insert("", "end", values=(name, ", ".join(risk_reasons)))

    # --- TAB 5: SETTINGS (FIXED SAFE SAVE) ---
    def create_settings_frame(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        ctk.CTkLabel(frame, text="System Settings", font=("Roboto", 28, "bold"), text_color=("black", "white")).pack(
            pady=(0, 20))

        card = ctk.CTkFrame(frame, fg_color=("white", "#1e1e1e"), corner_radius=10)
        card.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(card, text="Interface Theme", font=("Arial", 14), text_color=("black", "white")).grid(row=0,
                                                                                                           column=0,
                                                                                                           padx=20,
                                                                                                           pady=20,
                                                                                                           sticky="w")
        ctk.CTkOptionMenu(card, values=["Dark", "Light", "System"], command=ctk.set_appearance_mode).grid(row=0,
                                                                                                          column=1,
                                                                                                          padx=20,
                                                                                                          sticky="e")

        ctk.CTkLabel(card, text="Grading Criteria Weights (Must equal 1.0)", font=("Arial", 14, "bold"),
                     text_color="#3498db").grid(row=1, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        self.w_quiz_ent = self.create_config_entry(card, "Quiz Weight (0.0-1.0)", self.math.w_quiz, 2)
        self.w_mid_ent = self.create_config_entry(card, "Midterm Weight (0.0-1.0)", self.math.w_mid, 3)
        self.w_final_ent = self.create_config_entry(card, "Finals Weight (0.0-1.0)", self.math.w_final, 4)

        ctk.CTkButton(card, text="SAVE CONFIGURATION", command=self.save_settings, fg_color="#e67e22",
                      hover_color="#d35400").grid(row=5, column=1, padx=20, pady=20, sticky="e")

        return frame

    def create_config_entry(self, parent, label, value, r):
        ctk.CTkLabel(parent, text=label, font=("Arial", 12)).grid(row=r, column=0, padx=30, pady=5, sticky="w")
        ent = ctk.CTkEntry(parent, width=100)
        ent.grid(row=r, column=1, padx=20, pady=5, sticky="e")
        ent.insert(0, str(value))
        return ent

    def save_settings(self):
        try:
            q = float(self.w_quiz_ent.get())
            m = float(self.w_mid_ent.get())
            f = float(self.w_final_ent.get())

            if not (0 <= q <= 1) or not (0 <= m <= 1) or not (0 <= f <= 1):
                raise ValueError("Weights must be between 0.0 and 1.0")

            if round(q + m + f, 2) != 1.0:
                messagebox.showwarning("Math Error", f"Total weight is {q + m + f:.2f}. It must equal 1.0")
                return

            # SAFE JSON WRITING
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config',
                                       'settings.json')

            with open(config_path, 'r') as file:  # Use 'file' not 'f'
                current_data = json.load(file)

            current_data['grading_weights'] = {"quiz": q, "midterm": m, "final": f}

            with open(config_path, 'w') as file:
                json.dump(current_data, file, indent=4)

            if messagebox.askyesno("Restart Required",
                                   "Configuration saved successfully.\n\nNew grading weights will only apply after a restart.\n\nDo you want to restart the application now?"):
                self.destroy()
                os.execl(sys.executable, sys.executable, *sys.argv)

        except Exception as e:
            messagebox.showerror("Error", f"Invalid Input: {str(e)}")

    # --- TAB 6: ABOUT ---
    def create_about_frame(self):
        frame = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        ctk.CTkLabel(frame, text="About The System", font=("Roboto", 28, "bold"), text_color=("black", "white")).pack(
            pady=(0, 20))

        q_w = int(self.math.w_quiz * 100)
        m_w = int(self.math.w_mid * 100)
        f_w = int(self.math.w_final * 100)

        self.create_wiki_section(frame, "🎓", "System Overview",
                                 "EduMatrix is a smart academic tracking system designed to help teachers monitor performance.\n"
                                 "It combines database management with AI analytics to identify trends and predict student outcomes based on attendance.")

        self.create_wiki_section(frame, "🛠️", "How to Use",
                                 "1. Student Management:\n"
                                 "   - Go to 'Student Records' tab.\n"
                                 "   - Add students with their Attendance Rate (%) and Subject Grades.\n"
                                 f"   - The system auto-calculates Weighted GPA ({q_w}% Quiz, {m_w}% Midterm, {f_w}% Final).\n\n"
                                 "2. Data Intelligence:\n"
                                 "   - Go to 'Intelligence Hub'.\n"
                                 "   - Use the Regression Model to see how Attendance affects Grades.\n"
                                 "   - Use the Predictor Calculator to forecast grades for a specific attendance rate.\n"
                                 "   - Check 'Honors & Intervention' to see who is passing/failing.")

        self.create_wiki_section(frame, "💻", "Technical Specifications",
                                 "• Language: Python 3.10+\n"
                                 "• UI Framework: CustomTkinter\n"
                                 "• Database: SQLite3 (Normalized Schema)\n"
                                 "• AI Engine: SciPy (Linear Regression) & NumPy\n"
                                 "• Visualization: Matplotlib")

        self.create_wiki_section(frame, "🏆", "Development Team",
                                 "Coleco, Rob Ivan C.\n"
                                 "Cruz, Lou Philip B.\n"
                                 "Gonzales, John Austin L.\n"
                                 "Mallorca, Mj J.\n\n"
                                 "Section: BSIT 3-4\n"
                                 "Course: Event Driven Programming\n"
                                 "Pamantasan ng Lungsod ng Valenzuela (PLV)")

        return frame

    def create_wiki_section(self, parent, icon, title, content):
        card = ctk.CTkFrame(parent, fg_color=("white", "#1e1e1e"), corner_radius=10)
        card.pack(fill="x", pady=10, ipady=10)

        header_box = ctk.CTkFrame(card, fg_color="transparent")
        header_box.pack(anchor="w", padx=20, pady=(10, 5))

        ctk.CTkLabel(header_box, text=icon, font=("Arial", 24), width=30).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(header_box, text=title, font=("Arial", 16, "bold"), text_color="#3498db").pack(side="left")

        ctk.CTkLabel(card, text=content, font=("Arial", 13), text_color=("gray30", "gray80"), justify="left",
                     anchor="w").pack(anchor="w", padx=20, pady=(0, 10))