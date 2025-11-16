# ==========================
# IMPORTS
# ==========================
import tkinter as tk
from tkinter import messagebox, ttk
import random
import os

try:
    from tkvideo import tkvideo
except ImportError:
    messagebox.showerror("Error", "Please install tkvideo:\n pip install tkvideo")
    exit()

import pygame  # For background music and punchline sound

# ==========================
# JOKES DATA
# ==========================
jokes = {
    "easy": [
        ("Why did the chicken cross the road? 🐔", "To get to the other side! 🚶‍♂️"),
        ("What do you call a bear with no teeth? 🐻", "A gummy bear! 🍬"),
        ("Why did the banana go to the doctor? 🍌", "Because it wasn’t peeling well! 😷"),
        ("Why did the car get a flat tire? 🚗", "Because there was a fork in the road! 🍴"),
        ("How did the hipster burn his mouth? 😎", "He ate his pizza before it was cool! 🍕🔥")
    ],
    "medium": [
        ("Why did the math book look sad? 📚", "Because it had too many problems! ➗"),
        ("What do you call fake spaghetti? 🍝", "An impasta! 😆"),
        ("Why can't your nose be 12 inches long? 👃", "Because then it would be a foot! 🦶"),
        ("Why does the golfer wear two pants? ⛳", "Because he's afraid he might get a 'Hole-in-one.' 🏌️"),
        ("Why should you wear glasses to maths class? 🤓", "Because it helps with division! ➗")
    ],
    "hard": [
        ("Why do programmers prefer dark mode? 💻", "Because light attracts bugs! 🐛"),
        ("Why did the scarecrow win an award? 🌾", "Because he was outstanding in his field! 🏆"),
        ("Why did the coffee file a police report? ☕", "It got mugged! 😱"),
        ("Why did the developer go broke? 💰", "Because he used up all his cache. 💾"),
        ("What do you call a dinosaur with only one eye? 🦖", "A Do-you-think-he-saw-us! 👀")
    ]
}

# ==========================
# MAIN JOKE APP
# ==========================
class JokeApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes("-fullscreen", True)

        # Background video
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bg_video_path = os.path.join(script_dir, "jokepage.mp4")
        self.video_label = tk.Label(root)
        self.video_label.place(x=0, y=0, relwidth=1, relheight=1)
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.bg_video = tkvideo(bg_video_path, self.video_label, loop=0, size=(screen_width, screen_height))
        self.bg_video.play()

        # Content frame
        main_frame = tk.Frame(root, bg="#FF8C42", bd=5, relief="ridge")
        main_frame.place(relx=0.5, rely=0.58, anchor="center")
        self.main_frame = main_frame  # store for timer placement

        self.levels = ["easy", "medium", "hard"]
        self.current_level_index = 0
        self.current_level = self.levels[self.current_level_index]
        self.index = 0
        self.current_joke = None

        # TIMER VARIABLES
        self.timer_value = 7
        self.timer_running = False

        # Timer label (top-right inside box)
        self.timer_label = tk.Label(
            main_frame,
            text="⏳ 7",
            font=("Comic Sans MS", 20, "bold"),
            bg="#FF8C42",
            fg="#8B0035"
        )
        self.timer_label.place(relx=0.95, rely=0.05, anchor="ne")

        # Level label
        self.level_label = tk.Label(main_frame, text=f"Level: {self.current_level.title()}",
                                    font=("Comic Sans MS", 28, "bold"),
                                    bg="#FF8C42", fg="#831943")
        self.level_label.pack(pady=10)

        # Joke setup
        self.setup_label = tk.Label(main_frame, text="", font=("Comic Sans MS", 22, "bold"),
                                    wraplength=1000, justify="center", bg="#FF8C42")
        self.setup_label.pack(pady=25)

        # Punchline
        self.punch_label = tk.Label(main_frame, text="", font=("Comic Sans MS", 22, "italic","bold"),
                                    wraplength=1000, justify="center", fg="#FF0793", bg="#FF8C42")
        self.punch_label.pack(pady=20)

        # Progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("green.Horizontal.TProgressbar", troughcolor='#FF8C42', 
                        background='#FF1493', thickness=25)
        self.progress = ttk.Progressbar(main_frame, style="green.Horizontal.TProgressbar", 
                                        orient="horizontal", length=600, mode="determinate")
        self.progress.pack(pady=15)
        self.update_progress_bar()

        # Buttons
        frame = tk.Frame(main_frame, bg="#FF8C42")
        frame.pack(pady=20)
        self.create_button(frame, "🎤 Tell me a joke", self.tell_joke, 0)
        self.create_button(frame, "😆 Punchline", self.show_punch, 1)
        self.create_button(frame, "➡ Next", self.next_joke, 2)
        self.create_button(frame, "❌ Quit", self.confirm_quit, 3)

    # -------------------------------
    # TIMER FUNCTIONS
    # -------------------------------
    def start_timer(self):
        self.timer_running = True
        self.timer_value = 7
        self.timer_label.config(text=f"⏳ {self.timer_value}")
        self.countdown()

    def stop_timer(self):
        self.timer_running = False

    def countdown(self):
        if not self.timer_running:
            return

        if self.timer_value > 0:
            self.timer_label.config(text=f"⏳ {self.timer_value}")
            self.timer_value -= 1
            self.root.after(1000, self.countdown)
        else:
            self.timer_label.config(text="⏳ 0")
            self.show_punch(auto=True)

    # -------------------------------

    def create_button(self, parent, text, command, column):
        btn = tk.Button(parent, text=text, font=("Tahoma", 16, "bold"),
                        bg="#23C4C4", fg="white", padx=15, pady=8,
                        command=command, activebackground="#1CA3A3", activeforeground="white")
        btn.grid(row=0, column=column, padx=15)
        btn.bind("<Enter>", lambda e: btn.config(bg="#1CA3A3"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#23C4C4"))

    # Animate text
    def animate_text(self, label, text, index=0):
        if index <= len(text):
            label.config(text=text[:index])
            self.root.after(30, lambda: self.animate_text(label, text, index+1))

    # Show setup
    def tell_joke(self):
        self.current_joke = jokes[self.current_level][self.index]
        self.punch_label.config(text="")

        self.animate_text(self.setup_label, self.current_joke[0])

        # Start 7-sec timer
        self.start_timer()

    # Show punchline
    def show_punch(self, auto=False):
        if not self.current_joke:
            messagebox.showinfo("⏳ Wait!", "Click 'Tell me a joke' first! 😅")
            return

        # Stop the timer if user clicks manually
        self.stop_timer()

        self.animate_text(self.punch_label, self.current_joke[1])

        # Play punchline sound
        punch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "punchline.mp3")
        if os.path.exists(punch_path):
            sound = pygame.mixer.Sound(punch_path)
            sound.play()
        else:
            messagebox.showwarning("⚠️ Audio Missing", f"Punchline audio not found: {punch_path} 😢")

    # Next joke
    def next_joke(self):
        self.stop_timer()

        self.index += 1
        if self.index >= len(jokes[self.current_level]):
            if self.current_level_index + 1 < len(self.levels):
                self.current_level_index += 1
                self.current_level = self.levels[self.current_level_index]
                self.index = 0
                self.level_up_animation()
            else:
                messagebox.showinfo("🔄 Restart", "All levels completed! Restarting Easy… 🐣")
                self.current_level_index = 0
                self.current_level = "easy"
                self.index = 0

        self.level_label.config(text=f"Level: {self.current_level.title()}")
        self.update_progress_bar()
        self.tell_joke()

    # Progress bar update
    def update_progress_bar(self):
        total = sum(len(jokes[l]) for l in self.levels)
        done = sum(len(jokes[self.levels[i]]) for i in range(self.current_level_index)) + self.index
        self.progress["maximum"] = total
        self.progress["value"] = done

    # Confirm quit
    def confirm_quit(self):
        result = messagebox.askyesno("❌ Exit Fun", "Are you sure you want to exit the fun? 😭")
        if result:
            self.root.destroy()

    # -------------------------------
    # LEVEL UP ANIMATION (KEPT SAME)
    # -------------------------------
    def level_up_animation(self):
        canvas = tk.Canvas(self.root, width=self.root.winfo_screenwidth(),
                           height=self.root.winfo_screenheight(), bg="#FF8C42", highlightthickness=0)
        canvas.place(x=0, y=0)

        level_emojis = {"EASY": ["🤣","🦆","🍕","🐸","😂"],
                        "MEDIUM": ["😂","😎","🤖","🦄"],
                        "HARD": ["🔥","💥","💣","⚡"]}

        confetti = []
        for _ in range(200):
            x = random.randint(0, self.root.winfo_screenwidth())
            y = random.randint(-800, 0)
            size = random.randint(20, 40)
            emoji = random.choice(level_emojis.get(self.current_level.upper(), ["✨"]))
            confetti.append([canvas.create_text(x, y, text=emoji, font=("Arial", size)),
                             random.randint(3, 12),
                             random.choice([-2, 2])])

        def animate_confetti():
            for c, speed, dx in confetti:
                canvas.move(c, dx, speed)
                pos = canvas.coords(c)
                if pos[1] > self.root.winfo_screenheight():
                    canvas.move(c, 0, -self.root.winfo_screenheight() - random.randint(20, 100))
            self.root.after(50, animate_confetti)

        animate_confetti()

        banner = canvas.create_text(
            self.root.winfo_screenwidth() // 2, -100,
            text=f"LEVEL UP! {self.current_level.upper()}",
            font=("Comic Sans MS", 60, "bold"),
            fill="#831943"
        )

        def animate_banner(y=-100):
            if y < self.root.winfo_screenheight() // 4:
                y += 10
                canvas.coords(banner, self.root.winfo_screenwidth() // 2, y)
                self.root.after(50, lambda: animate_banner(y))
            else:
                pulse_banner(1.0)

        def pulse_banner(scale):
            if scale < 1.5:
                canvas.itemconfig(banner, font=("Comic Sans MS", int(60 * scale), "bold"))
                scale += 0.05
                self.root.after(100, lambda: pulse_banner(scale))
            else:
                fade_banner(1.0)

        def fade_banner(alpha):
            if alpha > 0:
                try:
                    canvas.itemconfig(banner, fill=f"#FF1493{int(alpha * 255):02x}")
                except:
                    pass
                self.root.after(100, lambda: fade_banner(alpha - 0.05))
            else:
                canvas.delete(banner)

        animate_banner()

        def flash_bg(times=0):
            if times < 8:
                canvas.config(bg=random.choice(["#FFF59D", "#FFCCBC", "#B2DFDB", "#E1BEE7"]))
                self.root.after(150, lambda: flash_bg(times + 1))
            else:
                canvas.config(bg="#FF8C42")

        flash_bg()

        self.root.after(5500, lambda: canvas.destroy())

        messagebox.showinfo("🎉 Level Up!", f"Welcome to {self.current_level.upper()} level! 🚀")

# ==========================
# START PAGE
# ==========================
class StartPage:
    def __init__(self, root):
        self.root = root
        self.root.attributes("-fullscreen", True)
        self.root.title("Alexa Joke Assistant 🤖")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        video_path = os.path.join(script_dir, "randoms.mp4")

        self.video_label = tk.Label(root)
        self.video_label.pack(fill="both", expand=True)

        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        self.player = tkvideo(video_path, self.video_label, loop=1, size=(w, h))
        self.player.play()

        self.start_btn = tk.Button(root, text=" Let’s Go! 🚀", font=("Tahoma", 18, "bold"),
                                   bg="#831943", fg="white", padx=25, pady=12,
                                   activebackground="#9B1D59", activeforeground="white",
                                   command=self.open_main_app)
        self.start_btn.place(relx=0.305, rely=0.7, anchor="center")
        self.start_btn.bind("<Enter>", lambda e: self.start_btn.config(bg="#9B1D59"))
        self.start_btn.bind("<Leave>", lambda e: self.start_btn.config(bg="#831943"))

    def open_main_app(self):
        self.video_label.destroy()
        self.start_btn.destroy()
        JokeApp(self.root)

# ==========================
# RUN APP
# ==========================
if __name__ == "__main__":
    pygame.mixer.init()
    root = tk.Tk()

    music_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "background.mp3")
    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)
    else:
        messagebox.showwarning("⚠️ Music Missing", f"Background music not found: {music_path} 😢")

    StartPage(root)
    root.mainloop()
