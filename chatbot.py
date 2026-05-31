import tkinter as tk
import random
import datetime
import webbrowser
import re
import os

# ---------------- WINDOW ----------------
root = tk.Tk()
root.title("Mimi AI Assistant 🐧✨")
root.geometry("550x750")
root.resizable(False, False)

# ---------------- BACKGROUND CANVAS ----------------
canvas = tk.Canvas(root, width=550, height=750, bg="#0b0f19", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# ---------------- COLORS ----------------
colors = ["#00f5ff", "#ff4dff", "#ffe066", "#4dff88", "#ff6b6b", "#6ea8ff"]

# ---------------- PARTICLES ----------------
particles = []

for i in range(60):
    x = random.randint(0, 550)
    y = random.randint(0, 750)
    size = random.randint(2, 4)

    color = random.choice(colors)

    obj = canvas.create_oval(x, y, x+size, y+size, fill=color, outline="")
    dx = random.choice([-2, -1, 1, 2])
    dy = random.choice([-2, -1, 1, 2])

    particles.append([obj, dx, dy])

def animate():
    for p in particles:
        obj, dx, dy = p

        canvas.move(obj, dx, dy)
        x1, y1, x2, y2 = canvas.coords(obj)

        if x1 <= 0 or x2 >= 550:
            p[1] = -p[1]
        if y1 <= 0 or y2 >= 750:
            p[2] = -p[2]

    root.after(25, animate)

animate()

# ---------------- CHAT BOX ----------------
chat_box = tk.Text(root, bg="#111827", fg="white",
                   font=("Arial", 12), wrap="word")
chat_box.place(x=20, y=20, width=510, height=520)

chat_box.insert(tk.END, "🐧 Mimi: Hello! I'm your AI Assistant ✨🤖\n")
chat_box.config(state=tk.DISABLED)

# ---------------- INPUT ----------------
frame = tk.Frame(root, bg="#0b0f19")
canvas.create_window(275, 650, window=frame)

entry = tk.Entry(frame, font=("Arial", 14), width=30)
entry.pack(side=tk.LEFT, ipady=6)

# ---------------- CHAT FUNCTION ----------------
def add_chat(sender, msg):
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, f"\n{sender}: {msg}\n")
    chat_box.config(state=tk.DISABLED)
    chat_box.see(tk.END)

# ---------------- SMART AI FUNCTION ----------------
def send_message(event=None):
    user = entry.get().lower().strip()
    entry.delete(0, tk.END)

    add_chat("You", user)

    words = set(user.split())
    response = ""

    # ---------------- GREETINGS ----------------
    if words & {"hi", "hello", "hey", "heyy"}:
        response = random.choice([
            "Hello 😄✨",
            "Hi there 👋🤖",
            "Heyy buddy 🌟"
        ])

    # ---------------- HOW ARE YOU ----------------
    elif ("how" in words and "you" in words) or "how r you" in user:
        response = "I'm doing great 😄 thanks for asking!"

    # ---------------- WHAT ARE YOU DOING ----------------
    elif ("what" in words and "doing" in words) or "whats up" in user or "what's up" in user:
        response = random.choice([
            "I'm chatting with you 🤖💬",
            "Just helping you right now ✨",
            "Thinking about AI stuff 😎",
            "Waiting for your commands 🚀"
        ])

    # ---------------- FOOD / BREAKFAST / ACTIVITY FIX ----------------
    elif any(word in words for word in ["eat", "eating", "food", "breakfast", "lunch", "dinner"]):
        response = random.choice([
            "Yummy 😋 hope you enjoyed it!",
            "Food time is the best time 🍕✨",
            "I wish I could eat too 🤖🍔"
        ])

    elif any(word in words for word in ["had", "did", "doing", "today", "day"]):
        response = random.choice([
            "Sounds like a nice day 😊",
            "Hope your day is going well 🌟",
            "Tell me more 🤖✨"
        ])

    # ---------------- WHO ARE YOU ----------------
    elif "who" in words and "you" in words:
        response = "I'm Mimi 🐧 your cute AI assistant 🤖✨"

    # ---------------- TIME / DATE ----------------
    elif "time" in words:
        response = f"⏰ {datetime.datetime.now().strftime('%I:%M %p')}"

    elif "date" in words:
        response = f"📅 {datetime.datetime.now().strftime('%d-%m-%Y')}"

    # ---------------- GOOGLE ----------------
    elif "google" in words:
        webbrowser.open("https://google.com")
        response = "🌐 Opening Google..."

    # ---------------- YOUTUBE ----------------
    elif "youtube" in words:
        webbrowser.open("https://youtube.com")
        response = "📺 Opening YouTube..."

    # ---------------- APPS ----------------
    elif "notepad" in words:
        os.system("notepad")
        response = "📝 Opening Notepad..."

    elif "calculator" in words:
        os.system("calc")
        response = "🔢 Opening Calculator..."

    # ---------------- WIKIPEDIA ----------------
    elif "wiki" in words:
        topic = user.replace("wiki", "").strip()
        if topic:
            webbrowser.open(f"https://en.wikipedia.org/wiki/{topic}")
            response = f"📚 Searching Wikipedia for {topic}"
        else:
            response = "🤔 Tell me a topic!"

    # ---------------- MATH ----------------
    elif any(op in user for op in "+-*/"):
        try:
            expr = re.findall(r"[0-9+\-*/().%]+", user)
            result = eval("".join(expr))
            response = f"🧮 Answer: {result}"
        except:
            response = "❌ I couldn't calculate that!"

    # ---------------- EXIT ----------------
    elif "bye" in words:
        response = "👋 Goodbye! See you soon 💙"

    # ---------------- DEFAULT ----------------
    else:
        response = random.choice([
            "🤖 I'm still learning new things!",
            "✨ Try: hello, time, google, wiki",
            "😅 I didn't understand that yet"
        ])

    add_chat("Mimi", response)

# ---------------- BUTTON ----------------
btn = tk.Button(frame, text="Send 🚀", command=send_message,
                bg="#ff6b6b", fg="white", font=("Arial", 12))
btn.pack(side=tk.RIGHT, padx=5)

# ---------------- ENTER KEY ----------------
root.bind("<Return>", send_message)

# ---------------- CLEAR CHAT ----------------
clear_btn = tk.Button(root, text="Clear 🧹",
                      command=lambda: chat_box.delete(1.0, tk.END),
                      bg="#4dff88", fg="black")
clear_btn.place(x=20, y=700)

# ---------------- RUN ----------------
root.mainloop()