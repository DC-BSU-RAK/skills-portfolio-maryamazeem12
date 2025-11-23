import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import random
import os
import pygame  # For audio playback

# ==========================
# GLOBAL VARIABLES
# ==========================
score = 0  # Player score
question_number = 0  # Current question number
current_answer = 0  # Correct answer for the current question
difficulty = 1  # Difficulty level (1=easy, 2=moderate, 3=advanced)
max_questions = 10  # Total questions per game
second_chance = True  # Allows one retry per question
timer_seconds = 15  # Timer per question
timer_id = None  # ID for the after() method controlling timer

# Video loop IDs for scheduling video playback
start_after_id = None
instruction_after_id = None
difficulty_after_id = None
result_after_id = None

# ==========================
# WORKING DIRECTORY
# ==========================
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)  # Ensure all file paths are relative to script

# ==========================
# MAIN WINDOW SETUP
# ==========================
root = tk.Tk()
root.title("🎉 Fun Maths Quiz 🎉")
root.attributes('-fullscreen', True)  # Fullscreen mode
root.attributes('-topmost', True)  # Keep window on top
root.overrideredirect(True)  # Remove default window frame
root.bind("<Escape>", lambda e: root.destroy())  # Escape closes app

# Get screen dimensions
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# ==========================
# AUDIO SETUP
# ==========================
pygame.mixer.init()  # Initialize pygame audio
intro_music_path = "intro_music.mp3"
quiz_music_path = "quiz_music.mp3"
correct_audio_path = "correct.mp3"
wrong_audio_path = "wrong.mp3"

# Play background music
def play_music(path, loop=-1, volume=0.5):
    if os.path.exists(path):
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loop)

# Stop background music
def stop_music():
    pygame.mixer.music.stop()

# Play short sound effects
def play_sound(path, volume=1.0):
    if os.path.exists(path):
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        sound.play()

# ==========================
# CANVAS AND FRAMES
# ==========================
canvas = tk.Canvas(root, width=screen_width, height=screen_height, highlightthickness=0)
canvas.pack(fill="both", expand=True)  # Main canvas covering entire window

# Frames for different pages
menu_frame = tk.Frame(root, bg="#222")
quiz_frame = tk.Frame(root, bg="#222")
result_frame = tk.Frame(root, bg="#222")
next_page_frame = tk.Frame(root, bg="#222")
difficulty_frame = tk.Frame(root, bg="#222")

# ==========================
# VIDEO CAPTURE INITIALIZATION
# ==========================
def init_videos():
    global cap_start, instructions_cap, difficulty_cap, result_cap

    # Safely create video capture object if file exists
    def safe_capture(file):
        if os.path.exists(file):
            return cv2.VideoCapture(file)
        else:
            print(f"Warning: Video file '{file}' not found.")
            return None

    cap_start = safe_capture("quiz2.mp4")
    instructions_cap = safe_capture("instructions.mp4")
    difficulty_cap = safe_capture("levels.mp4")
    result_cap = safe_capture("result_bg.mp4")

init_videos()

# ==========================
# VIDEO PLAYBACK FUNCTIONS
# ==========================
def play_video(cap, canvas_widget, bg_id, after_var_name, frame_img_var_name):
    """Plays video frames on the given canvas using after() loop."""
    if cap is None:
        return

    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (screen_width, screen_height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        globals()[frame_img_var_name] = ImageTk.PhotoImage(img)
        canvas_widget.itemconfig(bg_id, image=globals()[frame_img_var_name])
    # Schedule next frame update
    globals()[after_var_name] = canvas_widget.after(30, lambda: play_video(cap, canvas_widget, bg_id, after_var_name, frame_img_var_name))

# ==========================
# START PAGE
# ==========================
start_bg_id = canvas.create_image(0, 0, anchor="nw", image=None)
start_frame_img = None

def play_start_video():
    play_video(cap_start, canvas, start_bg_id, "start_after_id", "start_frame_img")

def create_play_button():
    """Creates the PLAY button on the start page with hover effect."""
    x1, y1 = screen_width//2 - 80, int(screen_height*0.65)-35
    x2, y2 = screen_width//2 + 80, int(screen_height*0.65)+35
    dark_yellow = "#FFD700"

    # Button shape and text
    oval = canvas.create_oval(x1, y1, x2, y2, fill="black", outline=dark_yellow, width=3, tags="playbtn")
    text = canvas.create_text(screen_width//2, int(screen_height*0.65), text="PLAY ▶", fill=dark_yellow,
                              font=("Helvetica", 20, "bold"), tags="playbtn")

    # Hover effects
    def on_enter(event):
        canvas.itemconfig(oval, fill=dark_yellow)
        canvas.itemconfig(text, fill="black")
    def on_leave(event):
        canvas.itemconfig(oval, fill="black")
        canvas.itemconfig(text, fill=dark_yellow)

    canvas.tag_bind(oval, "<Enter>", on_enter)
    canvas.tag_bind(oval, "<Leave>", on_leave)
    canvas.tag_bind(text, "<Enter>", on_enter)
    canvas.tag_bind(text, "<Leave>", on_leave)

    # Click event to move to instructions page
    def click(event):
        if cap_start: cap_start.release()
        canvas.pack_forget()
        next_page_frame.pack(fill="both", expand=True)
        play_instructions_video()
        create_next_button()

    canvas.tag_bind(oval, "<Button-1>", click)
    canvas.tag_bind(text, "<Button-1>", click)

# ==========================
# INSTRUCTIONS PAGE
# ==========================
instructions_canvas = tk.Canvas(next_page_frame, width=screen_width, height=screen_height, highlightthickness=0)
instructions_canvas.pack(fill="both", expand=True)
instructions_bg_id = instructions_canvas.create_image(0, 0, anchor="nw", image=None)
instructions_frame_img = None

def play_instructions_video():
    play_video(instructions_cap, instructions_canvas, instructions_bg_id, "instruction_after_id", "instructions_frame_img")

def create_next_button():
    """Creates NEXT button for instructions page with hover effect."""
    x1, y1 = int(screen_width*0.65) - 80, int(screen_height*0.85) - 35
    x2, y2 = int(screen_width*0.65) + 80, int(screen_height*0.85) + 35
    med_yellow = "#DAA520"

    oval = instructions_canvas.create_oval(x1, y1, x2, y2, fill="black", outline=med_yellow, width=3, tags="nextbtn")
    text = instructions_canvas.create_text(int(screen_width*0.65), int(screen_height*0.85),
                                           text="NEXT ➡", fill=med_yellow, font=("Helvetica", 20, "bold"), tags="nextbtn")

    def on_enter(event):
        instructions_canvas.itemconfig(oval, fill=med_yellow)
        instructions_canvas.itemconfig(text, fill="black")
    def on_leave(event):
        instructions_canvas.itemconfig(oval, fill="black")
        instructions_canvas.itemconfig(text, fill=med_yellow)

    instructions_canvas.tag_bind(oval, "<Enter>", on_enter)
    instructions_canvas.tag_bind(oval, "<Leave>", on_leave)
    instructions_canvas.tag_bind(text, "<Enter>", on_enter)
    instructions_canvas.tag_bind(text, "<Leave>", on_leave)

    # Click event to go to difficulty selection page
    def click(event):
        if instructions_cap: instructions_cap.release()
        next_page_frame.pack_forget()
        difficulty_frame.pack(fill="both", expand=True)
        play_difficulty_video()
        create_difficulty_buttons()

    instructions_canvas.tag_bind(oval, "<Button-1>", click)
    instructions_canvas.tag_bind(text, "<Button-1>", click)

# ==========================
# DIFFICULTY PAGE
# ==========================
difficulty_canvas = tk.Canvas(difficulty_frame, width=screen_width, height=screen_height, bg="#111", highlightthickness=0)
difficulty_canvas.pack(fill="both", expand=True)
difficulty_bg_id = difficulty_canvas.create_image(0, 0, anchor="nw", image=None)
difficulty_frame_img = None

def play_difficulty_video():
    play_video(difficulty_cap, difficulty_canvas, difficulty_bg_id, "difficulty_after_id", "difficulty_frame_img")

def create_difficulty_buttons():
    """Creates difficulty buttons with hover effect and click logic."""
    difficulty_canvas.delete("diffbtn")
    options = [
        ("Easy (1-digit) 🐣", 1, "#6aff6a", "#00b300"),
        ("Moderate (2-digit) 🐱", 2, "#ffd966", "#ff9900"),
        ("Advanced (4-digit) 🦄", 3, "#ff6ab3", "#ff1a75")
    ]
    start_y = int(screen_height * 0.40)
    gap = 100

    for i, (text, level, color_top, color_bottom) in enumerate(options):
        y = start_y + i * gap
        left, right = screen_width//2 - 200, screen_width//2 + 200
        top, bottom = y - 35, y + 35
        shadow = difficulty_canvas.create_rectangle(left+6, top+6, right+6, bottom+6,
                                                    fill="#000000", outline="", tags=("diffbtn", f"shadow_{i}"))
        rect = difficulty_canvas.create_rectangle(left, top, right, bottom,
                                                  fill=color_top, outline=color_bottom, width=3, tags=("diffbtn", f"rect_{i}"))
        txt = difficulty_canvas.create_text(screen_width//2, y, text=text, font=("Arial", 24, "bold"), fill="white", tags=("diffbtn", f"text_{i}"))

        # Hover enter
        def make_on_enter(r=rect, s=shadow, t=txt, top_c=color_top):
            def _on_enter(event):
                difficulty_canvas.itemconfig(r, fill=top_c)
                difficulty_canvas.itemconfig(s, fill=top_c)
                difficulty_canvas.itemconfig(t, fill="#000")
            return _on_enter

        # Hover leave
        def make_on_leave(r=rect, s=shadow, t=txt, top_c=color_top):
            def _on_leave(event):
                difficulty_canvas.itemconfig(r, fill=top_c)
                difficulty_canvas.itemconfig(s, fill="#000")
                difficulty_canvas.itemconfig(t, fill="white")
            return _on_leave

        for part in [rect, shadow, txt]:
            difficulty_canvas.tag_bind(part, "<Enter>", make_on_enter())
            difficulty_canvas.tag_bind(part, "<Leave>", make_on_leave())

        # Click to start quiz at selected difficulty
        def make_click(lvl):
            def _click(event):
                if lvl == 1:
                    msg = "There are 10 single-digit questions.\nAre you ready? 🎉"
                elif lvl == 2:
                    msg = "There are 10 two-digit questions.\nAre you ready? 🎉"
                else:
                    msg = "There are 10 four-digit questions.\nAre you ready? 🎉"
                answer = messagebox.askquestion("Start Level?", msg)
                if answer == "yes":
                    global difficulty
                    difficulty = lvl
                    if difficulty_cap: difficulty_cap.release()
                    difficulty_frame.pack_forget()
                    stop_music()
                    play_music(quiz_music_path, loop=-1, volume=0.4)
                    start_quiz(difficulty)
            return _click

        click_handler = make_click(level)
        for part in [rect, shadow, txt]:
            difficulty_canvas.tag_bind(part, "<Button-1>", click_handler)

# ==========================
# QUIZ PAGE
# ==========================
quiz_canvas = tk.Canvas(quiz_frame, width=screen_width, height=screen_height, highlightthickness=0)
quiz_canvas.pack(fill="both", expand=True)

# Background image for quiz
quiz_bg_path = os.path.join(script_dir, "quiz_bg.jpg")
if os.path.exists(quiz_bg_path):
    quiz_bg_img = Image.open(quiz_bg_path).resize((screen_width, screen_height), Image.Resampling.LANCZOS)
    quiz_bg_photo = ImageTk.PhotoImage(quiz_bg_img)
    quiz_canvas.bg_image_ref = quiz_bg_photo
    quiz_canvas.create_image(0, 0, anchor="nw", image=quiz_canvas.bg_image_ref)
else:
    quiz_canvas.create_rectangle(0, 0, screen_width, screen_height, fill="black")
    print(f"Warning: Quiz background not found at {quiz_bg_path}")

# Labels and frames for questions, timer, options
question_number_label = tk.Label(quiz_canvas, text="", font=("Comic Sans MS", 24, "bold"),
                                 fg="#f1c40f", bg="#bb2413", width=15)
question_number_label.place(relx=0.5, rely=0.12, anchor="n")

question_frame = tk.Frame(quiz_canvas, bg="#ff6b6b", width=600, height=200)
question_frame.place(relx=0.5, rely=0.22, anchor="n")
question_frame.pack_propagate(False)

question_label = tk.Label(question_frame, text="", font=("Comic Sans MS", 36, "bold"),
                          bg="#ff6b6b", fg="white")
question_label.pack(expand=True)

# Timer label (emoji + number with no gap)
timer_label = tk.Label(
    question_frame,
    text="⏳15",  # emoji directly next to number
    font=("Segoe UI Emoji", 24, "bold"),  # emoji-friendly font
    fg="yellow",
    bg="#ff6b6b"
)
timer_label.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

# Options frame
options_frame = tk.Frame(quiz_canvas, bg="#ec3b27")
options_frame.place(relx=0.5, rely=0.5, anchor="n")
option_buttons = []

# Feedback and score labels
feedback_label = tk.Label(quiz_canvas, text="", font=("Comic Sans MS",18), fg="orange", bg="#222")
feedback_label.place(relx=0.5, rely=0.75, anchor="center")

score_label = tk.Label(quiz_canvas, text="Score: 0", font=("Helvetica",21), fg="black", bg="#ff6b6b")
score_label.place(relx=0.5, rely=0.85, anchor="center")

# ==========================
# QUIZ LOGIC + TIMER
# ==========================
def display_options(options):
    """Displays answer buttons for the current question."""
    global option_buttons
    for btn in option_buttons:
        btn.destroy()
    option_buttons = []
    for i, opt in enumerate(options):
        btn = tk.Button(options_frame, text=opt, font=("Arial", 18, "bold"),
                        width=5, height=2, bg="#f8c291", fg="black",
                        command=lambda val=opt: check_answer(val))
        btn.grid(row=0, column=i, padx=10)
        option_buttons.append(btn)

def random_int():
    """Generates two random numbers based on difficulty level."""
    if difficulty == 1:
        return random.randint(0,9), random.randint(0,9)
    elif difficulty == 2:
        return random.randint(10,99), random.randint(10,99)
    else:
        return random.randint(1000,9999), random.randint(1000,9999)

def decide_operation():
    """Randomly selects addition or subtraction."""
    return random.choice(['+','-'])

def start_timer():
    """Starts the countdown timer for a question."""
    global timer_seconds, timer_id
    timer_seconds = 15
    def countdown():
        global timer_seconds, timer_id
        if timer_seconds >= 0:
            timer_label.config(text=f"⏱️ {timer_seconds}")
            if timer_seconds <= 5:
                timer_label.config(fg="red")
            else:
                timer_label.config(fg="yellow")
            timer_seconds -= 1
            timer_id = quiz_frame.after(1000, countdown)
        else:
            feedback_label.config(text=f"❌ Time's up! The answer was {current_answer}", fg="black", bg="#f44336")
            play_sound(wrong_audio_path)
            quiz_frame.after(1200, next_question)
    countdown()

def next_question():
    """Loads the next question or ends quiz if max_questions reached."""
    global num1, num2, operation, current_answer, question_number, second_chance, timer_id
    feedback_label.config(text="")
    second_chance = True
    if timer_id: quiz_frame.after_cancel(timer_id)
    if question_number >= max_questions:
        stop_music()
        show_final_score()
        return
    num1, num2 = random_int()
    operation = decide_operation()
    current_answer = num1 + num2 if operation == '+' else num1 - num2
    options = [current_answer, current_answer + random.randint(1,5), current_answer - random.randint(1,5)]
    random.shuffle(options)
    question_number_label.config(text=f"Question {question_number + 1}/{max_questions}")
    question_label.config(text=f"{num1} {operation} {num2} = ? 🤔")
    display_options(options)
    question_number += 1
    start_timer()

def check_answer(ans):
    """Checks user's answer and updates score/feedback."""
    global score, second_chance, timer_id
    if timer_id: quiz_frame.after_cancel(timer_id)
    if ans == current_answer:
        score += 10 if second_chance else 5
        feedback_label.config(text="🎉 Correct! 👍", fg="#31DA56", bg="#f86150")
        score_label.config(text=f"Score: {score}")
        play_sound(correct_audio_path)
        quiz_canvas.after(1200, next_question)
    else:
        if second_chance:
            feedback_label.config(text="❌ Oops! Try Again! 💡", fg="yellow", bg="#f44336")
            play_sound(wrong_audio_path)
            second_chance = False
            start_timer()
        else:
            feedback_label.config(text=f"❌ Wrong! The answer was {current_answer}", fg="black", bg="#f44336")
            play_sound(wrong_audio_path)
            quiz_canvas.after(1200, next_question)

def start_quiz(level):
    """Initializes quiz at selected difficulty."""
    global difficulty, score, question_number
    difficulty = level
    score = 0
    question_number = 0
    difficulty_frame.pack_forget()
    quiz_frame.pack(fill="both", expand=True)
    score_label.config(text=f"Score: {score}")
    feedback_label.config(text="")
    next_question()

# ==========================
# RESULT PAGE
# ==========================
result_canvas = tk.Canvas(result_frame, width=screen_width, height=screen_height, highlightthickness=0)
result_canvas.pack(fill="both", expand=True)
result_bg_id = result_canvas.create_image(0, 0, anchor="nw", image=None)
result_frame_img = None

def play_result_video():
    play_video(result_cap, result_canvas, result_bg_id, "result_after_id", "result_frame_img")

# Result label and buttons
result_label = tk.Label(result_canvas, text="", font=("Helvetica", 28),
                        fg="white", bg="black", justify="center")
result_label.place(relx=0.35, rely=0.55, anchor="center")

play_again_btn = tk.Button(result_canvas, text="Play Again ▶", font=("Helvetica", 20),
                           bg="black", fg="#FFD700", bd=3, relief="raised")
play_again_btn.place(relx=0.30, rely=0.7, anchor="center")

quit_btn = tk.Button(result_canvas, text="Quit ❌", font=("Helvetica", 20),
                     bg="black", fg="#FFD700", bd=3, relief="raised")
quit_btn.place(relx=0.43, rely=0.7, anchor="center")

# Hover effects for result buttons
def on_enter_play(event): play_again_btn.config(bg="#FFD700", fg="black")
def on_leave_play(event): play_again_btn.config(bg="black", fg="#FFD700")
play_again_btn.bind("<Enter>", on_enter_play)
play_again_btn.bind("<Leave>", on_leave_play)

def on_enter_quit(event): quit_btn.config(bg="#FFD700", fg="black")
def on_leave_quit(event): quit_btn.config(bg="black", fg="#FFD700")
quit_btn.bind("<Enter>", on_enter_quit)
quit_btn.bind("<Leave>", on_leave_quit)

# Quit button logic
def quit_quiz():
    answer = messagebox.askquestion("Quit Quiz", "Do you really want to quit? 🛑")
    if answer == "yes":
        root.destroy()
    else:
        result_frame.pack_forget()
        canvas.pack(fill="both", expand=True)
        play_again()

quit_btn.config(command=quit_quiz)

# Display final score and rank
def show_final_score():
    quiz_frame.pack_forget()
    result_frame.pack(fill="both", expand=True)
    play_result_video()
    final_score = min(int((score / (max_questions*10)) * 100), 100)
    if final_score >= 90:
        rank = "A+ 🌟"
        msg = "You're a Maths Genius! 🧠✨"
    elif final_score >= 80:
        rank = "A 🎉"
        msg = "Great Job! Keep it up! 💪"
    elif final_score >= 70:
        rank = "B 👍"
        msg = "Well Done! You can do better! 😊"
    else:
        rank = "C 😅"
        msg = "Keep Practicing! You got this! 💡"
    result_label.config(text=f"Score: {score}/{max_questions*10}\nRank: {rank}\n{msg}")

# Play again logic
def play_again():
    global cap_start, instructions_cap, difficulty_cap, result_cap
    global start_after_id, instruction_after_id, difficulty_after_id, result_after_id

    # Cancel any running video loops
    if start_after_id: canvas.after_cancel(start_after_id)
    if instruction_after_id: instructions_canvas.after_cancel(instruction_after_id)
    if difficulty_after_id: difficulty_canvas.after_cancel(difficulty_after_id)
    if result_after_id: result_canvas.after_cancel(result_after_id)

    # Release video captures
    if cap_start: cap_start.release()
    if instructions_cap: instructions_cap.release()
    if difficulty_cap: difficulty_cap.release()
    if result_cap: result_cap.release()

    # Reinitialize videos
    init_videos()
    stop_music()
    play_music(intro_music_path, loop=-1, volume=0.9)
    result_frame.pack_forget()
    canvas.pack(fill="both", expand=True)
    create_play_button()
    play_start_video()

play_again_btn.config(command=play_again)

# ==========================
# START APPLICATION
# ==========================
play_music(intro_music_path, loop=-1, volume=0.9)  # Play intro music
play_start_video()  # Start video on start page
create_play_button()  # Display start button
root.mainloop()  # Launch main loop
