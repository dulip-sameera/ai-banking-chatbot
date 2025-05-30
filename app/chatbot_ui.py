import logging
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
from chatbot import Chatbot

        
class ChatbotUI:
    def __init__(self, root):
        print('Chatbot UI Initializing...')
        self.root = root
        self.root.title('Banking Assistant Chatbot')
        self.root.geometry('600x500')
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.chatbot = Chatbot()
        
        self.create_interface()
        
        self.display_msg("Banking Assistant", "Hello! I'm your banking assistant. How can I help you today?")
        print('Chatbot UI Initializing Completed')

    def create_interface(self):
            # chat display
            self.chat_view = scrolledtext.ScrolledText(
                self.root,
                wrap=tk.WORD,
                width=60,
                height=20,
                state='disabled'
            )
            self.chat_view.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
            
            self.user_input_text = tk.Entry(self.root, width=50)
            self.user_input_text.grid(row=1, column=0, padx=10, pady=10)
            self.user_input_text.bind("<Return>", lambda event: self.process_user_input())
            
            self.send_button = tk.Button(
                self.root,
                text="Send",
                command=self.process_user_input
            )
            self.send_button.grid(row=1, column=1, padx=10, pady=10)
            
            self.feedback_button = tk.Button(
                self.root,
                text="Give Feedback",
                command=self.get_feedback
            )
            self.feedback_button.grid(row=2, column=0, columnspan=2, pady=5)      
        
    def display_msg(self, sender, message):
        self.chat_view.config(state='normal')
        self.chat_view.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_view.config(state='disabled')
        self.chat_view.see(tk.END)
    
    def process_user_input(self):
        text = self.user_input_text.get().strip()
        if not text:
            return
        
        self.display_msg("You", text)
        self.user_input_text.delete(0, tk.END)
        
        self.chatbot.last_user_query = text
        
        response = self.chatbot.generate_response(text)
        self.chatbot.last_chatbot_response = response
        self.display_msg("Banking Assistant", response)    
            
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
            
    def on_close(self):
        self.chatbot.knowledgebase.db.connection_close()
        self.root.destroy()
            

                                  