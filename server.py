import socket
import tkinter as tk
import threading
import os
import tkinter.filedialog as tkfiledialog
import time
import select

# Flag indicating a data packet
DATA_PACKET_FLAG = b'1'  

# Flag indicating an acknowledgment packet
ACK_PACKET_FLAG = b'0' 

# Size of data payload in byte
payload_size = 1024      

# EWMA constant for calculating timeout
ALPHA = 0.125 

class ServerGUI:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.ServerSocket = None
        self.connections = []
        
        # Initialize GUI
        self.root = tk.Tk()
        self.root.title("Server")
        
        # Frame for displaying messages
        self.messages_frame = tk.Frame(self.root)
        self.messages_frame.pack(padx=10, pady=10)
        
        # Scrollbar for messages
        self.messages_scrollbar = tk.Scrollbar(self.messages_frame)
        self.messages_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget for displaying messages
        self.messages = tk.Text(self.messages_frame, height=15, width=50, bg="#f0f0f0", fg="#333", yscrollcommand=self.messages_scrollbar.set)
        self.messages.pack()
        self.messages_scrollbar.config(command=self.messages.yview)
        
        # Entry field for sending messages
        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack(pady=5)
        
        # Button for sending text messages
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message, bg="skyblue", fg="black", relief=tk.FLAT)
        self.send_button.pack(pady=5)
        
        # Button for sending files
        self.file_button = tk.Button(self.root, text="Send File", command=self.send_file, bg="skyblue", fg="black", relief=tk.FLAT)
        self.file_button.pack(pady=5)
        
        # Start server setup in a separate thread
        threading.Thread(target=self.setup_server).start()
        
    def setup_server(self):
        # Set up server socket and start listening for connections
        self.ServerSocket = socket.socket()
        self.ServerSocket.bind((self.host,self.port))
        self.ServerSocket.listen(5)
        
        while True:
            # Accept incoming connections and start a new thread for each
            connection, address = self.ServerSocket.accept()
            self.connections.append(connection)
            threading.Thread(target=self.receive_message, args=(connection,)).start()
    
    def send_acknoledgement(connection, filename, payload_size):
        # Function for sending acknowledgment to the client
        global timeout
        try:
            # File sending started

            # Start time for Round Trip Time (RTT) measurement
            RTT_start_time = time.time()
            with open(filename, 'rb') as file:
                data = file.read(payload_size)
                sequence_number = 1  
                while data:
                    connection.sendall(DATA_PACKET_FLAG + data)
                    print(f"Sent packet no: {sequence_number}")
                    
                    # Wait for acknowledgment with a timeout
                    ready = select.select([connection], [], [], 0.1)  
                    if ready[0]:
                        # Wait for acknowledgment from the client
                        ack_flag = connection.recv(1)
                        if ack_flag == ACK_PACKET_FLAG:
                            sequence_number += 1
                            data = file.read(payload_size)

                            # Calculate SampleRTT
                            RTT_end_time = time.time()
                            SampleRTT = (RTT_end_time - RTT_start_time)

                            # Update EWMA timeout using SampleRTT
                            timeout = (1 - ALPHA) * timeout + ALPHA * SampleRTT

                            # Start measuring RTT for the next packet
                            RTT_start_time = time.time()
                        else:
                            print("Error in acknowledgment. Resending...")
                            # On acknowledgment error, reset timeout to a default value
                            timeout = 0.1
                    else:
                        print("Timeout! Resending...")
                        # On timeout, reset timeout to a default value
                        timeout = 0.1
        except Exception as e:
            print(f"Error sending file: {e}")

    def receive_message(self, connection):
        # Function for receiving messages from clients
        while True:
            try:
                data = connection.recv(1024).decode()
                if data:
                    sender_name, message = data.split(":", 1)  
                    self.messages.insert(tk.END, sender_name + ': ' + message + '\n') 
                    if message.startswith("FILE:"):
                        filename = message.split(":")[1]
                        self.receive_file(connection, filename)
                    else:
                        # Broadcast the message to all connected clients
                        for conn in self.connections:
                            if conn != connection:
                                conn.send(data.encode())
            except Exception as e:
                print(e)
                break

    def receive_file(self, connection, filename):
        # Function for receiving files from clients
        try:
            with open(filename, "wb") as file:
                while True:
                    data = connection.recv(1024)
                    if not data:
                        break
                    file.write(data)
            self.messages.insert(tk.END, 'File received: ' + filename + '\n')
        except Exception as e:
            print(e)

    def send_message(self):
        # Function for sending text messages to clients
        message = self.entry.get()
        if message:
            self.messages.insert(tk.END, 'Me: ' + message + '\n')
            for connection in self.connections:
                connection.send(('Server: ' + message).encode())
            self.entry.delete(0, tk.END)

    def send_file(self):
        # Function for sending files to clients
        filename = tkfiledialog.askopenfilename()
        if filename:
            for connection in self.connections:
                connection.send(("FILE:" + os.path.basename(filename)).encode())
                with open(filename, "rb") as file:
                    data = file.read(1024)
                    while data:
                        connection.send(data)
                        data = file.read(1024)
            self.messages.insert(tk.END, 'File sent: ' + os.path.basename(filename) + '\n')


if __name__ == "__main__":
    # Start the server GUI
    try:
        server_gui = ServerGUI("127.0.0.1", 4553)
        server_gui.root.mainloop()
    except Exception as e:
        print(f"Error starting server GUI: {e}")