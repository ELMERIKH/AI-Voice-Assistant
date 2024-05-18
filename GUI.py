import tkinter as tk
from tkinter import ttk
from tkinter import messagebox,simpledialog,Checkbutton, IntVar
from tkinter.simpledialog import askstring
from tkinter import PhotoImage
import configparser
import pygame
import os
import cv2
from PIL import Image, ImageTk
from main import runchatbot, generate_response
import threading
import sys
import speech_recognition as sr
import time
import pyttsx3
from pystray import MenuItem as item
from pystray import Icon
import pystray
from multiprocessing import Process


class CustomDialog(simpledialog.Dialog):
    def body(self, master):
        self.configure(background='black')
        tk.Label(master, text="Please enter your API key:", bg='black', fg='white').grid(row=0)
        self.entry = tk.Entry(master)
        self.entry.grid(row=1)
        return self.entry

    def apply(self):
        self.result = self.entry.get()


class ChatbotGUI:

    def __init__(self, root):

        self.root = root
        self.video_player = VideoPlayer(root, "./bb.gif",1)

        self.root.overrideredirect(True)
        self.root.bind("<ButtonPress-1>", self.start_drag)
        self.root.bind("<ButtonRelease-1>", self.stop_drag)
        self.root.bind("<B1-Motion>", self.on_drag)
        
       
        self.stop_event = threading.Event()

        bottom_frame = tk.Frame(self.root, bg="black")
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        self.response_box = tk.Text(self.root, height=5, width=50, bg="black", fg="#4ee44e")
        self.response_box.pack()
        self.run_button = tk.Button(self.root, text="RUN", command=self.start_chatbot_thread, bg="#179b17")
        self.run_button.pack(side=tk.BOTTOM)
        self.close_button = tk.Button(self.root, text="📌", command=self.minimize_to_icon, font=("Arial", 12), bg="red", fg="black")
        self.close_button.pack()

        self.close_button.pack(side=tk.BOTTOM, pady=5)
        
        self.engine = pyttsx3.init()
        self.engine.connect('started-utterance', self.on_speak)
        self.engine.connect('finished-utterance', self.on_speak_finish)
        self.x = 0
        self.y = 0
        self.start_x = 0
        self.start_y = 0
        self.dragging = False
        self.icon = "Beryl.ico"
        self.lift=False
        tray_thread = threading.Thread(target=self.tray)
        tray_thread.start()
        
        
        

    
    def tray(self):
        
            def on_quit(icon, item):
                icon.stop()
                self.root.quit()

            def on_show(icon, item):
                self.root.deiconify()

            def on_hide(icon, item):
                self.root.withdraw()

            menu = (pystray.MenuItem('Quit', on_quit), pystray.MenuItem('Show', on_show), pystray.MenuItem('Hide', on_hide))
            self.icon = pystray.Icon("name", Image.open("Beryl.ico"), "Beryl", menu=menu)
            self.icon.run()
        

    
    
    

    # Bind the events to the transparent window
       
        
    def minimize_to_icon(self):
    # Get the position of the close button
        close_button_x, close_button_y = self.close_button.winfo_rootx(), self.close_button.winfo_rooty()

        # Adjust the position of the main window to hover over the button
        window_width = 100  # Adjust the desired width of the window
        window_height = 100  # Adjust the desired height of the window
        window_x = close_button_x - window_width // 2  # Adjust the X position to center the window over the button
        window_y = close_button_y - window_height - 10  # Adjust the Y position to place the window above the button

        self.lift = True
        self.root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

        # Adjust the position of the video player canvas
        self.video_player = VideoPlayer(self.root, "./bb.gif", 0.3)
        self.video_player.canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        transparent_window = tk.Toplevel()
        transparent_window.overrideredirect(True)

        # Remove window decorations and set transparency
        transparent_window.wm_attributes('-transparentcolor', 'grey')
        transparent_window.wm_attributes('-topmost', True) 
        transparent_window.wm_attributes('-toolwindow', True)
        transparent_window.attributes("-alpha", 0.5)
        transparent_window.geometry("300x400+1000+100")
        

        # Add the response box to the transparent window
        self.response_box = tk.Text(transparent_window, height=600, width=300, bg="grey", fg="teal", font=("Helvetica", 16))
        self.response_box.pack()
        
        # Bind event handler after creating transparent_window
        self.root.bind("<Double-Button-1>", lambda event: self.restore_from_icon(transparent_window, event=event))

        def bring_to_front():
            while not self.stop_event.is_set():
                self.root.lift()
                self.root.attributes('-topmost', 1)
                transparent_window.lift()
                transparent_window.attributes('-topmost', 1)
                time.sleep(0.1)

        bring_to_front_thread = threading.Thread(target=bring_to_front)
        if self.lift:
            bring_to_front_thread.start()
                
            # Ensure the thread is terminated when exiting the function
            

            
        

# To restore the window when needed:
    def restore_from_icon(self, transparent_window, event=None):
        transparent_window.destroy()
        self.lift=False
        self.response_box.destroy()
        self.video_player.canvas.destroy()
        self.root.geometry("600x600")
        
    def start_chatbot_thread(self):
        
        key,lama = self.prompt_api_key()

        chatbot_thread = threading.Thread(target=runchatbot, args=(self.handle_response, key,lama))
        chatbot_thread.start()

    def handle_response(self, response):
        # Clear the response box
        self.response_box.delete('1.0', tk.END)

        for letter in response:
            self.response_box.insert(tk.END, letter)
            self.response_box.see(tk.END)
            self.root.update_idletasks()
            time.sleep(0.05)
        self.response_box.insert(tk.END, "\n")
        

    def speak(self, text):
        # Create a new process for the speech
        speech_process = Process(target=self._speak, args=(text,))
        speech_process.start()

    def _speak(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def on_speak(self, name, location, length):
        self.response_box.configure(state='disabled')

    def on_speak_finish(self, name, completed):
        
        self.response_box.configure(state='normal')
        
        


    def prompt_api_key(self):
        config = configparser.ConfigParser()
        config_file = 'config.ini'

        if not os.path.exists(config_file):
            root = tk.Tk()
            root.withdraw()  # Hide the main window

            # Prompt for API key
            api_key_dialog = CustomDialog(root)

            # Create a Toplevel window for selecting Llama key
            top = tk.Toplevel()
            top.title("API Type")
            
            top.resizable(False, False)
            
            # Initialize IntVar to store the checkbox value
            is_lama_key = IntVar()

            # Create Checkbutton
            checkbtn = Checkbutton(top, text="Is this a Llama key?", variable=is_lama_key)
            checkbtn.pack(pady=10)

            # Function to handle button click
            def submit():
                top.destroy()  # Close the Toplevel window

            # Create Submit button
            submit_btn = tk.Button(top, text="Submit", command=submit)
            submit_btn.pack()

            # Wait for user interaction
            top.wait_window()

            # Get the value of the checkbox
            is_lama_key_value = bool(is_lama_key.get())
            print(is_lama_key_value)

            # Store the API key in the config file
            config['DEFAULT'] = {'API_Key': api_key_dialog.result, 'Is_Llama_Key': is_lama_key_value}
            with open(config_file, 'w') as f:
                config.write(f)
        else:
            config.read(config_file)
            api_key = config['DEFAULT']['API_Key']
            is_lama_key_value = config.getboolean('DEFAULT', 'Is_Llama_Key')

        return api_key, is_lama_key_value
    
    def start_drag(self, event):
        self.dragging = True
        self.last_x = event.x_root
        self.last_y = event.y_root

    def on_drag(self, event):
        if self.dragging:
            deltax = event.x_root - self.last_x
            deltay = event.y_root - self.last_y
            new_x = self.root.winfo_x() + deltax
            new_y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{new_x}+{new_y}")
            self.last_x = event.x_root
            self.last_y = event.y_root

    def stop_drag(self, event):
        self.dragging = False

class VideoPlayer:
    def __init__(self, parent, video_source, scale_factor=0.5):
        self.parent = parent
        self.video_source = video_source
        self.cap = cv2.VideoCapture(self.video_source)
        self.original_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.original_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.scale_factor = scale_factor
        self.width = int(self.original_width * self.scale_factor)
        self.height = int(self.original_height * self.scale_factor)
        self.canvas = tk.Canvas(self.parent, width=self.original_width, height=self.original_height, highlightbackground="black", bg='black')
        self.canvas.pack()

        self.delay = 80
        self.update()
        # Set up sound
        self.sound_file = "/misc.mp3"

    def update(self):
        ret, frame = self.cap.read()
        if not ret:
            # restart the video from the beginning
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()

        if ret:
            # Resize the frame
            resized_frame = cv2.resize(frame, (self.width, self.height))

            img = Image.fromarray(resized_frame)
            img_tk = ImageTk.PhotoImage(image=img)

            self.canvas.img_tk = img_tk
            self.canvas.create_image((self.original_width - self.width) // 2, (self.original_height - self.height) // 2, anchor=tk.NW, image=img_tk)

        self.parent.after(self.delay, self.update)

    def play_sound(self):
        # Load sound file
        pygame.mixer.init()
        pygame.mixer.music.load(self.sound_file)

        # Play sound in loop
        pygame.mixer.music.play(-1)

    def submit_text(self):
        # Get text from widget3
        text = self.widget3.get()

        # Show message box with text
        messagebox.showinfo("Input Text", f"You entered: {text}")
    

def main():
    root = tk.Tk()
    root.title("Beryl")
    root.configure(bg="black")
    
    # def on_quit(icon, item):
    #     icon.stop()
    #     root.quit()

    # def on_show(icon, item):
    #     root.deiconify()

    # def on_hide(icon, item):
    #     root.withdraw()

    # menu = (item('Quit', on_quit), item('Show', on_show), item('Hide', on_hide))
    # icon = pystray.Icon("name", Image.open("img.png"), "Beryl", menu=menu)
    # icon.run()
    
    gui = ChatbotGUI(root)
    root.iconbitmap("./Beryl.ico")

    

    root.mainloop()


if __name__ == '__main__':
    main()
