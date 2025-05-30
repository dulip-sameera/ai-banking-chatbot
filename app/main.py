import nltk
from dotenv import load_dotenv
import tkinter as tk
from chatbot_ui import ChatbotUI

# Download NLTK data
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('stopwords')

load_dotenv("../app/.env")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotUI(root)
    root.mainloop()  
            
