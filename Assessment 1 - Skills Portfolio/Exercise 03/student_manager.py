import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import os
import random

FILENAME = "studentMarks.txt"

# -----------------------------
# Load and Save Students
# -----------------------------
def load_students():
    students = []
    try:
        with open(FILENAME, "r") as f:
            lines = [line for line in f if line.strip()]  # ignore empty lines
            for line in lines[1:]:  # skip the first line (number of students)
                parts = line.strip().split(",")
                if len(parts) == 6:  # make sure all fields exist
                    students.append({
                        "id": parts[0].strip(),
                        "name": parts[1].strip(),
                        "c1": int(parts[2].strip()),
                        "c2": int(parts[3].strip()),
                        "c3": int(parts[4].strip()),
                        "exam": int(parts[5].strip())
                    })
    except FileNotFoundError:
        messagebox.showerror("Error", f"{FILENAME} not found!")
    return students


students = load_students()  # Initialize students list

def save_students():
    # Save all student records to the file
    with open(FILENAME, "w") as f:
        f.write(str(len(students)) + "\n")  # Save total count
        for s in students:
            f.write(f"{s['id']},{s['name']},{s['c1']},{s['c2']},{s['c3']},{s['exam']}\n")

# -----------------------------
# Calculations
# -----------------------------
def total_coursework(s): return s["c1"] + s["c2"] + s["c3"]  # Sum of coursework
def overall_percentage(s): return (total_coursework(s)+s["exam"])/160*100  # Total % based on 160
def grade(p):
    # Determine grade based on percentage
    if p >= 70: return "A"
    if p >= 60: return "B"
    if p >= 50: return "C"
    if p >= 40: return "D"
    return "F"
def grade_color(p):
    # Return color code for grade
    if p >= 80: 
        return "#0B640B"   # Green
    elif p >= 50: 
        return "#FF8C00"   # Orange
    else: 
        return "#B03030"   # Red

# -----------------------------
# Display Helper
# -----------------------------
def display(text, color_map=None):
    # Display text in scrolled text box, optionally with colors
    output.config(state="normal")
    output.delete(1.0, tk.END)
    if not color_map:
        output.insert(tk.END, text)
    else:
        for part, color in color_map:
            output.insert(tk.END, part, ("bold_color",))
            output.tag_config("bold_color", foreground=color, font=("Helvetica", 12, "bold"))
    output.config(state="disabled")

# -----------------------------
# Student Management Functions
# -----------------------------
def view_all(shuffle=True):
    # Display all students, optionally shuffled
    if not students:
        display("No student records available.")
        return

    display_list = students.copy()
    if shuffle:
        random.shuffle(display_list)

    text, color_map = "", []
    total_percent = 0

    for i, s in enumerate(display_list, start=1):
        percent = overall_percentage(s)
        total_percent += percent

        part = (f"{i}. Student\n"
                f"Name: {s['name']}\nID: {s['id']}\nCoursework Total: {total_coursework(s)} / 60\n"
                f"Exam: {s['exam']} / 100\nOverall %: {percent:.2f}%\nGrade: {grade(percent)}\n"
                "-----------------------------\n")

        text += part
        color_map.append((part, grade_color(percent)))

    avg = total_percent / len(students)
    summary = f"\nTotal students: {len(students)}\nAverage Percentage: {avg:.2f}%"
    text += summary
    color_map.append((summary, "#000000"))

    display(text, color_map)
    refresh_stats()

def view_individual():
    # Search and display individual student
    query = simpledialog.askstring("Search", "Enter student ID or name:")
    if not query: return
    query = query.strip().lower()
    results = [s for s in students if s["id"].strip() == query or query in s["name"].strip().lower()]
    if not results:
        messagebox.showinfo("Not found", "Student does not exist.")
        return
    text, color_map = "", []
    for i, s in enumerate(results, start=1):
        percent = overall_percentage(s)
        part = (f"{i}. Student\n"
                f"Name: {s['name']}\nID: {s['id']}\nCoursework Total: {total_coursework(s)} / 60\n"
                f"Exam: {s['exam']} / 100\nOverall %: {percent:.2f}%\nGrade: {grade(percent)}\n"
                "-----------------------------\n")
        text += part
        color_map.append((part, grade_color(percent)))
    display(text, color_map)

def highest_mark():
    # Show student with highest overall %
    if not students: return
    s = max(students, key=overall_percentage)
    percent = overall_percentage(s)
    part = f"Highest Scoring Student:\n\nName: {s['name']}\nID: {s['id']}\nOverall %: {percent:.2f}%\nGrade: {grade(percent)}"
    display(part, [(part, "#0B640B")])

def lowest_mark():
    # Show student with lowest overall %
    if not students: return
    s = min(students, key=overall_percentage)
    percent = overall_percentage(s)
    part = f"Lowest Scoring Student:\n\nName: {s['name']}\nID: {s['id']}\nOverall %: {percent:.2f}%\nGrade: {grade(percent)}"
    display(part, [(part, "#B03030")])

def sort_students():
    # Sort students ascending or descending based on overall %
    choice = simpledialog.askstring("Sort", "Enter 'asc' or 'desc':")
    if not choice or choice.lower() not in ["asc","desc"]:
        messagebox.showerror("Error", "Invalid input.")
        return
    students.sort(key=overall_percentage, reverse=(choice.lower()=="desc"))
    save_students()
    view_all(shuffle=False)

def add_student():
    # Add new student record
    try:
        sid = simpledialog.askstring("Add", "Student ID:").strip()
        name = simpledialog.askstring("Add", "Name:").strip()
        c1 = int(simpledialog.askstring("Add", "Coursework 1:"))
        c2 = int(simpledialog.askstring("Add", "Coursework 2:"))
        c3 = int(simpledialog.askstring("Add", "Coursework 3:"))
        exam = int(simpledialog.askstring("Add", "Exam:"))
        students.append({"id": sid, "name": name, "c1": c1, "c2": c2, "c3": c3, "exam": exam})
        save_students()
        messagebox.showinfo("Added", "Student added successfully.")
        view_all()
    except:
        messagebox.showerror("Error", "Invalid input.")

def delete_student():
    # Delete a student by ID or name
    query = simpledialog.askstring("Delete", "Enter student ID or name:").strip().lower()
    for s in students:
        if s["id"].strip() == query or query in s["name"].strip().lower():
            students.remove(s)
            save_students()
            messagebox.showinfo("Deleted", "Student removed.")
            view_all()
            return
    messagebox.showinfo("Not found", "Student does not exist.")
    
def update_student():
    # Search student by ID or name
    query = simpledialog.askstring("Update", "Enter student ID or Name:").strip().lower()
    if not query:
        return

    matched_students = [s for s in students if s["id"].strip() == query or query in s["name"].strip().lower()]
    if not matched_students:
        messagebox.showinfo("Not Found", "Student does not exist.")
        return

    s = matched_students[0]  # Take the first match
    try:
        # Ask for new values in a message box; leave blank to keep old value
        new_c1 = simpledialog.askstring("Update", f"CW1 ({s['c1']}): Leave blank to keep")
        new_c2 = simpledialog.askstring("Update", f"CW2 ({s['c2']}): Leave blank to keep")
        new_c3 = simpledialog.askstring("Update", f"CW3 ({s['c3']}): Leave blank to keep")
        new_exam = simpledialog.askstring("Update", f"Exam ({s['exam']}): Leave blank to keep")

        # Update only if input provided
        if new_c1: s['c1'] = int(new_c1)
        if new_c2: s['c2'] = int(new_c2)
        if new_c3: s['c3'] = int(new_c3)
        if new_exam: s['exam'] = int(new_exam)

        save_students()  # Save updated data
        messagebox.showinfo("Updated", f"{s['name']}'s record updated successfully!")
        view_all()  # Refresh output display
    except ValueError:
        messagebox.showerror("Error", "Invalid input! Marks must be numbers.")

def update_student():
    # Search student by ID or name
    query = simpledialog.askstring("Update", "Enter student ID or Name:").strip().lower()
    if not query:
        return

    matched_students = [s for s in students if s["id"].strip() == query or query in s["name"].strip().lower()]
    if not matched_students:
        messagebox.showinfo("Not Found", "Student does not exist.")
        return

    s = matched_students[0]  # Take the first match

    # Create a pop-up window
    popup = tk.Toplevel(root)
    popup.title(f"Update {s['name']}'s Record")
    popup.geometry("400x350")
    popup.configure(bg="#1A472A")

    # Labels and entries
    labels = ["Student ID", "Name", "Coursework 1", "Coursework 2", "Coursework 3", "Exam"]
    keys = ["id", "name", "c1", "c2", "c3", "exam"]
    entries = {}

    for i, (label, key) in enumerate(zip(labels, keys)):
        tk.Label(popup, text=label, font=("Helvetica", 12, "bold"), fg="#F5F5DC", bg="#1A472A").grid(row=i, column=0, padx=15, pady=10, sticky="w")
        entry = tk.Entry(popup, font=("Helvetica", 12))
        entry.grid(row=i, column=1, padx=15, pady=10)
        entry.insert(0, str(s[key]))  # pre-fill with existing value
        entries[key] = entry

    # Function to save updates
    def save_updates():
        try:
            # Update values from entries
            s["id"] = entries["id"].get().strip()
            s["name"] = entries["name"].get().strip()
            s["c1"] = int(entries["c1"].get())
            s["c2"] = int(entries["c2"].get())
            s["c3"] = int(entries["c3"].get())
            s["exam"] = int(entries["exam"].get())
            save_students()
            messagebox.showinfo("Updated", f"{s['name']}'s record updated successfully!")
            popup.destroy()
            view_all()  # Refresh main output
        except ValueError:
            messagebox.showerror("Error", "Invalid input! Marks must be numbers.")

    # Save button
    save_btn = tk.Button(popup, text="Save Changes", font=("Helvetica", 14, "bold"),
                         bg="#F5F5DC", fg="#0E3B2B", width=15, height=2,
                         relief="ridge", bd=3, command=save_updates)
    save_btn.grid(row=len(labels), column=0, columnspan=2, pady=20)

    # Optional: Make popup modal
    popup.grab_set()
    popup.focus_set()



# -----------------------------
# GUI Setup
# -----------------------------
root = tk.Tk()
root.title("Academic Portal")
root.attributes("-fullscreen", True)  # Fullscreen window
root.configure(bg="#0E3B2B")  # Dark green background

# -----------------------------
# Start Page
# -----------------------------
start_frame = tk.Frame(root)
start_frame.pack(fill="both", expand=True)

# Load background image if exists
image_path = os.path.join(os.path.dirname(__file__), "start.jpg")
if os.path.exists(image_path):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    img = Image.open(image_path).resize((screen_width, screen_height))
    bg_img = ImageTk.PhotoImage(img)
    bg_label = tk.Label(start_frame, image=bg_img)
    bg_label.image = bg_img
    bg_label.place(relwidth=1, relheight=1)

# Start button to open teacher login page
start_button = tk.Button(start_frame, text="Open", font=("Helvetica", 22, "bold"),
                         bg="#1A472A", fg="#F5F5DC", width=10, height=1,
                         relief="solid", bd=4,
                         command=lambda: switch_frame(teacher_frame))
start_button.place(relx=0.74, rely=0.66, anchor="center")
start_button.bind("<Enter>", lambda e: start_button.config(bg="#2E7D32"))
start_button.bind("<Leave>", lambda e: start_button.config(bg="#1A472A"))

# -----------------------------
# Teacher Login Page
# -----------------------------
teacher_frame = tk.Frame(root, bg="#1A472A")
teacher_header = tk.Label(teacher_frame, text="Teacher Verification", font=("Helvetica", 28, "bold"),
                          fg="#F5F5DC", bg="#1A472A")
teacher_header.pack(pady=30)

info_label = tk.Label(teacher_frame, text="Enter code to continue:",
                      font=("Helvetica", 16), fg="#F5F5DC", bg="#1A472A")
info_label.pack(pady=20)
teacher_code_var = tk.StringVar()
teacher_entry = tk.Entry(teacher_frame, textvariable=teacher_code_var, font=("Helvetica", 16), width=20)
teacher_entry.pack(pady=10)

def verify_teacher_code():
    # Verify code (any input allowed)
    code = teacher_code_var.get().strip()
    if not code:
        messagebox.showwarning("Input Required", "Please enter any code to continue!")
        return
    switch_frame(dashboard_frame)

verify_button = tk.Button(teacher_frame, text="Enter Dashboard", font=("Helvetica", 16, "bold"),
                          bg="#1A472A", fg="#F5F5DC", width=18, height=1,
                          relief="solid", bd=4, command=verify_teacher_code)
verify_button.pack(pady=20)
verify_button.bind("<Enter>", lambda e: verify_button.config(bg="#2E7D32"))
verify_button.bind("<Leave>", lambda e: verify_button.config(bg="#1A472A"))

back_button = tk.Button(teacher_frame, text="Back", font=("Helvetica", 12, "bold"),
                        bg="#F5F5DC", fg="#1A472A", width=10, height=1,
                        relief="solid", command=lambda: switch_frame(start_frame))
back_button.pack(pady=10)

# -----------------------------
# Dashboard Page
# -----------------------------
dashboard_frame = tk.Frame(root, bg="#0E3B2B")

header = tk.Label(dashboard_frame, text="Academic Portal", font=("Helvetica", 32, "bold"),
                  fg="#F5F5DC", bg="#0E3B2B")
header.pack(pady=20)

main_frame = tk.Frame(dashboard_frame, bg="#0E3B2B")
main_frame.pack(fill="both", expand=True, padx=20, pady=10)

# -----------------------------
# Left: Stats
# -----------------------------
stats_frame = tk.Frame(main_frame, bg="#0E3B2B", width=250)
stats_frame.pack(side="left", fill="y", padx=(0,15), pady=10)
stats_frame.pack_propagate(0)

stats_title = tk.Label(stats_frame, text="Quick Stats", font=("Helvetica", 18, "bold"),
                       fg="#F5F5DC", bg="#0E3B2B")
stats_title.pack(pady=10)

# Labels to display stats
box_width, box_height = 24, 3
stats_bg = "#F5F5DC"

total_label = tk.Label(stats_frame, font=("Helvetica", 14, "bold"), fg="#0E3B2B",
                       bg=stats_bg, width=box_width, height=box_height, relief="raised", bd=3)
total_label.pack(pady=8)
avg_label = tk.Label(stats_frame, font=("Helvetica", 14, "bold"), fg="#0E3B2B",
                     bg=stats_bg, width=box_width, height=box_height, relief="raised", bd=3)
avg_label.pack(pady=8)
high_label = tk.Label(stats_frame, font=("Helvetica", 14, "bold"), fg="#0E3B2B",
                      bg=stats_bg, width=box_width, height=box_height, relief="raised", bd=3)
high_label.pack(pady=8)
low_label = tk.Label(stats_frame, font=("Helvetica", 14, "bold"), fg="#0E3B2B",
                     bg=stats_bg, width=box_width, height=box_height, relief="raised", bd=3)
low_label.pack(pady=8)

# -----------------------------
# Center: Action Buttons
# -----------------------------
action_frame = tk.Frame(main_frame, bg="#0E3B2B", width=400)
action_frame.pack(side="left", fill="y", padx=(0,15), pady=10)
action_frame.pack_propagate(0)

# --- Search Students Button ---
search_active = False
search_listbox = None

def toggle_search_list():
    # Show or hide student search list
    global search_active, search_listbox
    search_active = not search_active

    # Remove previous listbox and label
    for widget in action_frame.winfo_children():
        if isinstance(widget, tk.Listbox) or (isinstance(widget, tk.Label) and widget.cget("text")=="Select a Student"):
            widget.destroy()

    if search_active:
        # Hide other buttons
        for widget in action_frame.winfo_children():
            if isinstance(widget, tk.Button) and widget != search_btn:
                widget.grid_remove()

        lbl = tk.Label(action_frame, text="Select a Student", font=("Helvetica", 16, "bold"),
                       fg="#F5F5DC", bg="#0E3B2B")
        lbl.grid(row=1, column=0, columnspan=2, pady=10)

        search_listbox = tk.Listbox(action_frame, font=("Helvetica", 12), width=25, height=10)
        search_listbox.grid(row=2, column=0, columnspan=2, pady=5)

        for s in students:
            search_listbox.insert(tk.END, s["name"])

        def on_select(event):
            # Display selected student info
            selection = event.widget.curselection()
            if selection:
                index = selection[0]
                student = students[index]
                percent = overall_percentage(student)
                if percent >= 80:
                    color = "#0B640B"
                elif percent >= 50:
                    color = "#FF8C00"
                else:
                    color = "#B03030"
                part = (f"Name: {student['name']}\n"
                        f"ID: {student['id']}\n"
                        f"Coursework Total: {total_coursework(student)} / 60\n"
                        f"Exam: {student['exam']} / 100\n"
                        f"Overall %: {percent:.2f}%\n"
                        f"Grade: {grade(percent)}")
                display(part, [(part, color)])

        search_listbox.bind("<<ListboxSelect>>", on_select)
    else:
        # Restore buttons
        for widget in action_frame.winfo_children():
            if isinstance(widget, tk.Button) and widget != search_btn:
                widget.grid()

# Shadow frame for search button
search_shadow = tk.Frame(action_frame, bg="#0C2F24")
search_shadow.grid(row=0, column=0, columnspan=2, pady=(10,5), padx=3)

search_btn = tk.Button(search_shadow, text="Search", bg="#F5F5DC", fg="#0E3B2B",
                       font=("Helvetica", 15, "bold"), width=10, height=1,
                       relief="ridge", bd=3,
                       command=toggle_search_list)
search_btn.pack()
search_btn.bind("<Enter>", lambda e: search_btn.config(bg="#D1C4E9"))
search_btn.bind("<Leave>", lambda e: search_btn.config(bg="#F5F5DC"))

# --- Original Action Buttons ---
action_buttons = [
    ("View All Students", lambda: view_all(shuffle=True)),
    ("View Individual Record", view_individual),
    ("Add Student", add_student),
    ("Update Student", update_student),
    ("Delete Student", delete_student),
    ("Sort Students", sort_students),
    ("Highest Mark", highest_mark),
    ("Lowest Mark", lowest_mark),
]

for i, (text, cmd) in enumerate(action_buttons):
    # Create and place action buttons in a grid layout
    btn = tk.Button(action_frame, text=text, bg="#F5F5DC", fg="#0E3B2B",
                    font=("Helvetica", 12, "bold"), width=20, height=2,
                    command=cmd, relief="ridge", bd=3)
    btn.grid(row=1 + i%4, column=i//4, padx=5, pady=5, sticky="nsew")
    # Add hover effect
    btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#D1C4E9"))
    btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#F5F5DC"))

# -----------------------------
# Clear Output Function
# -----------------------------
def clear_output():
    # Clears the output text area
    output.config(state="normal")
    output.delete(1.0, tk.END)
    output.config(state="disabled")

# Clear Output Button with Shadow
clear_shadow = tk.Frame(action_frame, bg="#0C2F24")
clear_shadow.grid(row=5, column=0, columnspan=2, pady=(20,5))
clear_btn = tk.Button(clear_shadow, text="Clear Output", font=("Helvetica", 14, "bold"),
                      bg="#F2F76F", fg="#0E3B2B", width=13, height=2,
                      relief="ridge", bd=3, command=clear_output)
clear_btn.pack()
clear_btn.bind("<Enter>", lambda e: clear_btn.config(bg="#D1C4E9"))
clear_btn.bind("<Leave>", lambda e: clear_btn.config(bg="#F5F5DC"))

# -----------------------------
# Right: Output Display
# -----------------------------
output_frame = tk.Frame(main_frame, bg="#0E3B2B")
output_frame.pack(side="left", fill="both", expand=True)
output = scrolledtext.ScrolledText(output_frame, font=("Helvetica", 12), bg="#F5F5DC", fg="#0E3B2B")
output.pack(fill="both", expand=True, padx=5, pady=5)

# -----------------------------
# Stats Refresh
# -----------------------------
def refresh_stats():
    # Update the statistics labels with current data
    total_label.config(text=f"Total Students: {len(students)}")
    if students:
        avg = sum([overall_percentage(s) for s in students])/len(students)
        avg_label.config(text=f"Average %: {avg:.2f}")
        high_label.config(text=f"Highest %: {max([overall_percentage(s) for s in students]):.2f}")
        low_label.config(text=f"Lowest %: {min([overall_percentage(s) for s in students]):.2f}")
    else:
        avg_label.config(text="Average %: N/A")
        high_label.config(text="Highest %: N/A")
        low_label.config(text="Lowest %: N/A")

# -----------------------------
# Frame Switching
# -----------------------------
def switch_frame(frame):
    # Bring the selected frame to the front
    frame.tkraise()
    refresh_stats()

# Place all frames in the same location so they can be raised
for f in [start_frame, teacher_frame, dashboard_frame]:
    f.place(relwidth=1, relheight=1)

# Start the application with the start frame
switch_frame(start_frame)
root.mainloop()
