import logging
import tkinter as tk
from tkinter import messagebox, simpledialog
from chatbot import Chatbot


class RoundedButton(tk.Canvas):
    """Custom Rounded Button for Tkinter"""
    def __init__(self, parent, text, radius=25, btn_width=120, height=40, color="#3f8be6", fg="#ffffff", font=("Segoe UI", 10), command=None):
        super().__init__(parent, bg=parent.cget("bg"), bd=0, highlightthickness=0, width=btn_width, height=height)
        self.radius = radius
        self.color = color
        self.fg = fg
        self.text = text
        self.command = command
        self.btn_width = btn_width
        self.height = height

        self.round_rect = self.create_rounded_rect(0, 0, btn_width, height, radius, fill=color)
        self.text_id = self.create_text(btn_width/2, height/2, text=text, fill=fg, font=font)

        self.bind("<ButtonPress-1>", lambda e: self.configure(relief="sunken"))
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)

    def create_rounded_rect(self, x1, y1, x2, y2, r=25, **kwargs):
        points = [x1 + r, y1,
                  x1 + r, y1,
                  x2 - r, y1,
                  x2 - r, y1,
                  x2, y1,
                  x2, y1 + r,
                  x2, y1 + r,
                  x2, y2 - r,
                  x2, y2 - r,
                  x2, y2,
                  x2 - r, y2,
                  x2 - r, y2,
                  x1 + r, y2,
                  x1 + r, y2,
                  x1, y2,
                  x1, y2 - r,
                  x1, y2 - r,
                  x1, y1 + r,
                  x1, y1 + r,
                  x1, y1]
        return self.create_polygon(points, smooth=True, outline="", **kwargs)

    def on_release(self, event):
        self.itemconfig(self.round_rect, fill=self.color)
        if self.command:
            self.command()

    def on_hover(self, event):
        self.itemconfig(self.round_rect, fill="#3570c6")

    def on_leave(self, event):
        self.itemconfig(self.round_rect, fill=self.color)


class ChatbotUI:
    def __init__(self, root):
        print('Chatbot UI Initializing...')
        self.root = root
        self.root.title('Banking Assistant Chatbot')
        self.root.geometry('900x650')
        self.root.minsize(700, 500)
        self.dark_mode = False

        # Theme Colors
        self.theme_colors = {
            "light": {
                "bg": "#f5f6fa",
                "fg": "#2f3640",
                "user_msg": "#d1e7dd",
                "bot_msg": "#f1f2f6",
                "entry_bg": "#ffffff",
                "border": "#cccccc"
            },
            "dark": {
                "bg": "#2f3640",
                "fg": "#f5f6fa",
                "user_msg": "#485460",
                "bot_msg": "#353b48",
                "entry_bg": "#404652",
                "border": "#555555"
            }
        }

        self.chatbot = Chatbot()
        self.messages = []  # Store message data for re-rendering
        self.last_canvas_width = 0  # Track last width to prevent unnecessary redraws

        self.create_interface()
        self.display_msg("Banking Assistant", "Hello! I'm your banking assistant. How can I help you today?")
        self.apply_theme() 
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Bind only once to avoid recursion
        self.root.bind("<Configure>", self.schedule_resize_update)
        print('Chatbot UI Initializing Completed')

    def create_interface(self):
        # Grid layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Chat Frame
        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Chat display (canvas + frame for message bubbles)
        self.chat_canvas = tk.Canvas(self.chat_frame, bd=0, highlightthickness=0)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.chat_frame, orient="vertical", command=self.chat_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")

        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.chat_inner_frame = tk.Frame(self.chat_canvas, bg=self.theme_colors["light"]["bg"])
        self.chat_window = self.chat_canvas.create_window((0, 0), window=self.chat_inner_frame, anchor="nw", width=100)

        # Input Area
        self.input_frame = tk.Frame(self.root)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.root.grid_rowconfigure(1, weight=0)

        self.user_input_text = tk.Entry(
            self.input_frame,
            font=("Segoe UI", 12),
            bd=1,
            relief="flat",
            highlightthickness=1,
            borderwidth=2
        )
        self.user_input_text.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.user_input_text.bind("<Return>", lambda event: self.process_user_input())

        self.send_button = RoundedButton(
            self.input_frame,
            text="Send",
            radius=15,
            btn_width=80,
            height=35,
            color="#3f8be6",
            fg="#ffffff",
            font=("Segoe UI", 10, "bold"),
            command=self.process_user_input
        )
        self.send_button.pack(side=tk.LEFT, padx=5)

        self.feedback_button = RoundedButton(
            self.input_frame,
            text="Feedback",
            radius=15,
            btn_width=90,
            height=35,
            color="#f39c12",
            fg="#ffffff",
            font=("Segoe UI", 10, "bold"),
            command=self.get_feedback
        )
        self.feedback_button.pack(side=tk.LEFT, padx=5)

        # Theme Toggle Button
        self.theme_button = RoundedButton(
            self.root,
            text="Toggle Theme",
            radius=15,
            btn_width=110,
            height=35,
            color="#7f8fa6",
            fg="#ffffff",
            font=("Segoe UI", 10, "bold"),
            command=self.toggle_theme
        )
        self.theme_button.grid(row=2, column=0, pady=10)

    def apply_theme(self):
        theme = "dark" if self.dark_mode else "light"
        colors = self.theme_colors[theme]

        self.root.configure(bg=colors["bg"])
        self.chat_frame.configure(bg=colors["bg"])
        self.chat_canvas.configure(bg=colors["bg"])
        self.chat_inner_frame.configure(bg=colors["bg"])
        self.msg_frame.configure(bg=colors["bg"])

        self.input_frame.configure(bg=colors["bg"])
        self.user_input_text.configure(
            bg=colors["entry_bg"],
            fg=colors["fg"],
            insertbackground=colors["fg"],
            highlightcolor="#3f8be6",
            highlightbackground=colors["border"]
        )

        # Reapply theme to existing messages
        for widget in self.chat_inner_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                for label in widget.winfo_children():
                    if isinstance(label, tk.Label):
                        sender = label.cget("text").split(":")[0]
                        if sender == "You":
                            label.configure(bg=colors["user_msg"], fg=colors["fg"])
                        else:
                            label.configure(bg=colors["bot_msg"], fg=colors["fg"])

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def toggle_input_state(self, state):
        """Enable or disable input field and buttons"""
        self.user_input_text.config(state=state)
        self.send_button.config(state=state)
        self.feedback_button.config(state=state)

    def display_msg(self, sender, message):
        self.messages.append((sender, message))
        self.redraw_messages()

    def schedule_resize_update(self, event=None):
        """Debounce resize event to prevent recursion"""
        if hasattr(self, "_resize_after"):
            self.root.after_cancel(self._resize_after)
        self._resize_after = self.root.after(100, self.on_window_resize)

    def on_window_resize(self, event=None):
        current_width = self.chat_canvas.winfo_width()
        if abs(current_width - self.last_canvas_width) > 10:
            self.last_canvas_width = current_width
            self.redraw_messages()

    def redraw_messages(self):
        # Clear current messages
        for widget in self.chat_inner_frame.winfo_children():
            widget.destroy()

        self.root.update_idletasks()  # Force update to get accurate width
        canvas_width = self.chat_canvas.winfo_width() - 40  # Account for padding

        for sender, message in self.messages:
            self._create_message_bubble(sender, message, canvas_width)

        self.chat_canvas.itemconfig(self.chat_window, width=canvas_width)
        self.update_chat_canvas_scrollregion()
        self.chat_canvas.yview_moveto(1.0)
        

    def _create_message_bubble(self, sender, message, canvas_width):
        self.msg_frame = tk.Frame(self.chat_inner_frame, bg=self.chat_inner_frame.cget("bg"))

        align = "e" if sender == "You" else "w"

        bg_color = self.theme_colors["dark" if self.dark_mode else "light"]["user_msg"] if sender == "You" else \
                   self.theme_colors["dark" if self.dark_mode else "light"]["bot_msg"]
        fg_color = self.theme_colors["dark" if self.dark_mode else "light"]["fg"]

        msg_label = tk.Label(
            self.msg_frame,
            text=f"{sender}: {message}",
            wraplength=min(canvas_width * 0.7, 400),  # Limit max width
            justify="left",
            bg=bg_color,
            fg=fg_color,
            padx=15,
            pady=8,
            font=("Segoe UI", 12),
            relief="flat",
            bd=0
        )
        msg_label.pack(anchor=align, side="top", padx=10, pady=5)

        self.msg_frame.pack(anchor=align, fill="x", padx=10, pady=2)

    def process_user_input(self):
        text = self.user_input_text.get().strip()
        self.user_input_text.delete(0, tk.END)
        if not text:
            return

        # Disable input until response comes
        self.toggle_input_state(tk.DISABLED)

        self.display_msg("You", text)
        

        self.chatbot.last_user_query = text

        # Simulate async behavior with after()
        self.root.after(100, self.generate_bot_response, text)

    def generate_bot_response(self, user_text):
        try:
            response = self.chatbot.generate_response(user_text)
            self.chatbot.last_chatbot_response = response
            self.display_msg("Banking Assistant", response)
        finally:
            # Always re-enable input
            self.toggle_input_state(tk.NORMAL)

    def get_feedback(self):
        if not self.chatbot.last_user_query or not self.chatbot.last_chatbot_response:
            messagebox.showinfo("Feedback", "No previous response to provide feedback on.")
            return

        feedback = simpledialog.askinteger(
            "Feedback",
            "How would you rate the last response? (1-5 where 5 is best)",
            parent=self.root,
            minvalue=1,
            maxvalue=5
        )

        if feedback:
            self.chatbot.train_model_from_feedback(
                self.chatbot.last_user_query,
                self.chatbot.last_chatbot_response,
                feedback
            )
            messagebox.showinfo("Feedback", "Thank you for your feedback!")

    def update_chat_canvas_scrollregion(self):
        self.chat_canvas.update_idletasks()
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

    def on_close(self):
        self.chatbot.knowledgebase.db.connection_close()
        self.root.destroy()