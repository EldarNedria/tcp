import socket
import threading
import sys, os
from tkinter import *
from tkinter import scrolledtext

print("Python version:", sys.version)
print("Working directory:", os.getcwd())

# GUI setup
root = Tk()
root.title("Chat Client")

# Center the window on the screen
window_width = 400
window_height = 330
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

# Function to toggle dark mode
def toggle_dark_mode():
    if dark_mode.get():
        root.config(bg='#2e2e2e')
        nickname_label.config(bg='#2e2e2e', fg='white')
        chat_label.config(bg='#2e2e2e', fg='white')
        message_label.config(bg='#2e2e2e', fg='white')
        chat_area.config(bg='#2e2e2e', fg='white', insertbackground='white')
        message_entry.config(bg='#2e2e2e', fg='white', insertbackground='white')
    else:
        root.config(bg='white')
        nickname_label.config(bg='white', fg='black')
        chat_label.config(bg='white', fg='black')
        message_label.config(bg='white', fg='black')
        chat_area.config(bg='white', fg='black', insertbackground='black')
        message_entry.config(bg='white', fg='black', insertbackground='black')

nickname_label = Label(root, text="Enter your nickname:")
nickname_label.pack(padx=10, pady=10)

nickname_entry = Entry(root, width=50)
nickname_entry.pack(padx=10, pady=10)

def connect_to_server():
    global nickname, client, stop_thread

    nickname = nickname_entry.get()
    if nickname == '':
        return

    nickname_label.pack_forget()
    nickname_entry.pack_forget()
    connect_button.pack_forget()
    dark_mode_check.pack_forget()

    chat_label.pack(padx=10, pady=10)
    chat_area.pack(expand=True, fill='both', padx=10, pady=10)
    message_label.pack(padx=10, pady=10)
    message_entry.pack(fill='x', padx=10, pady=10)
    send_button.pack(padx=10, pady=10)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 55555))

    stop_thread = False

    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

connect_button = Button(root, text="Connect", command=connect_to_server)
connect_button.pack(padx=10, pady=10)

dark_mode = BooleanVar()
dark_mode_check = Checkbutton(root, text="Dark Mode", variable=dark_mode, command=toggle_dark_mode)
dark_mode_check.pack(padx=10, pady=10)

chat_label = Label(root, text="Chat:")
chat_label.pack_forget()

chat_area = scrolledtext.ScrolledText(root, wrap=WORD, width=50, height=15)
chat_area.pack_forget()
chat_area.config(state=DISABLED)

message_label = Label(root, text="Message:")
message_label.pack_forget()

message_entry = Entry(root, width=50)
message_entry.pack_forget()

def send_message():
    message = f'{nickname}: {message_entry.get()}'
    if message[len(nickname) + 2:].startswith('/'):
        if nickname == 'admin':
            if message[len(nickname) + 2:].startswith('/kick'):
                client.send(f'KICK {message[len(nickname) + 2 + 6:]}'.encode('ascii'))
            elif message[len(nickname) + 2:].startswith('/ban'):
                client.send(f'BAN {message[len(nickname) + 2 + 5:]}'.encode('ascii'))
        else:
            chat_area.config(state=NORMAL)
            chat_area.insert(END, "Commands can be executed by Admins only!\n")
            chat_area.config(state=DISABLED)
    else:
        client.send(message.encode('ascii'))
    message_entry.delete(0, END)

send_button = Button(root, width= 20, text="Send", command=send_message)
send_button.pack_forget()

stop_thread = False

def receive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
                next_message = client.recv(1024).decode('ascii')
                if next_message == 'PASS':
                    password = input("Enter Password for Admin: ")
                    client.send(password.encode('ascii'))
                    if client.recv(1024).decode('ascii') == 'REFUSE':
                        chat_area.config(state=NORMAL)
                        chat_area.insert(END, "Connection is Refused !! Wrong Password\n")
                        chat_area.config(state=DISABLED)
                        stop_thread = True
                # Clients those are banned can't reconnect
                elif next_message == 'BAN':
                    chat_area.config(state=NORMAL)
                    chat_area.insert(END, "Connection Refused due to Ban\n")
                    chat_area.config(state=DISABLED)
                    client.close()
                    stop_thread = True
            else:
                chat_area.config(state=NORMAL)
                chat_area.insert(END, message + '\n')
                chat_area.config(state=DISABLED)
        except:
            chat_area.config(state=NORMAL)
            chat_area.insert(END, "Error Occurred while Connecting\n")
            chat_area.config(state=DISABLED)
            client.close()
            break

root.mainloop()