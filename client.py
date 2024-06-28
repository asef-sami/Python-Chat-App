import socket
import tkinter as tk
import threading
from tkinter import simpledialog
import time

DATA_PACKET_FLAG = b'1'  # Flag indicating a data packet
ACK_PACKET_FLAG = b'0'   # Flag indicating an acknowledgment packet

class ClientGUI:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.client_name = None 
        
        # Initialize GUI
        self.root = tk.Tk()
        self.get_client_name()
        self.root.title("Client: "+ self.client_name)
          
        # Frame for displaying messages
        self.messages_frame = tk.Frame(self.root)
        self.messages_frame.pack(padx=10, pady=10)
        
        # Scrollbar for messages
        self.messages_scrollbar = tk.Scrollbar(self.messages_frame)
        self.messages_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget for displaying messages
        self.messages = tk.Text(self.messages_frame, height=15, width=50, bg="lightgreen", fg="#333", yscrollcommand=self.messages_scrollbar.set)
        self.messages.pack()
        self.messages_scrollbar.config(command=self.messages.yview)
        
        # Entry field for sending messages
        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack(pady=5)
        
        # Button for sending text messages
        self.send_button = tk.Button(self.root, text="Send Message", command=self.send_message, bg="skyblue", fg="black", relief=tk.FLAT)
        self.send_button.pack(pady=5)
        
        # Start client setup in a separate thread
        threading.Thread(target=self.setup_client).start()

    def get_client_name(self):
        # Function for getting client's name
        try:
            self.client_name = simpledialog.askstring("Input", "Please enter your Name:")
        except Exception as e:
            print(f"Error getting client's name: {e}")

    def setup_client(self):
        # Set up client socket and connect to the server
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            threading.Thread(target=self.receive_message).start()
        except Exception as e:
            print(f"Error setting up client: {e}")

    def acknowledgment(conn, filename): 
        # Function for sending acknowledgment to the server
        try:
            with open(filename, 'wb') as file:
                sequence_number = 1
                data = conn.recv(1025)
                while data:
                    flag = data[0:1]
                    content = data[1:]

                    #print(f"Received successfully packet no : {sequence_number}")
                    if flag == DATA_PACKET_FLAG:
                        file.write(content)
                        # Send acknowledgment to the server
                        conn.sendall(ACK_PACKET_FLAG)
                        #print(f"Sent acknowledgement of packet no : {sequence_number}")
                        data = conn.recv(1025)
                        sequence_number+=1
                    else:
                        #Invalid packet received. Ignoring...
                        data = conn.recv(1025)
        except Exception as e:
            print(f"Error receiving file: {e}")

    def receive_message(self):
        # Function for receiving messages from the server
        while True:
            try:
                data = self.socket.recv(1024).decode()
                if data:
                    self.messages.insert(tk.END,data + '\n')  
                    if data.startswith("FILE:"):
                        filename = data.split(":")[1]
                        self.receive_file(filename)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def receive_file(self, filename):
        # Function for receiving files from the server
        try:
            save_filename = "received_" + filename  
            start_time = time.time()
            with open(save_filename, "wb") as file:
                while True:
                    data = self.socket.recv(1024)
                    if not data:
                        break
                    file.write(data)
                    if time.time() - start_time >= 5:
                        break
            self.messages.insert(tk.END, 'File received from Server: ' + save_filename + '\n')
        except Exception as e:
            print(f"Error receiving file: {e}")

    def send_message(self):
        # Function for sending text messages to the server
        try:
            message = self.entry.get()
            if message:
                full_message = f'{self.client_name}: {message}'
                self.messages.insert(tk.END, 'Me: ' + message + '\n')
                self.socket.send(full_message.encode())
                self.entry.delete(0, tk.END)
        except Exception as e:
            print(f"Error sending message: {e}")

if __name__ == "__main__":
    # Start the client GUI
    try:
        client_gui = ClientGUI("127.0.0.1", 4553)
        client_gui.root.mainloop()
    except Exception as e:
        print(f"Error starting client GUI: {e}")
