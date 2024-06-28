# Python-Chat-App
CSE 3101 Computer Networking course Project
# File Transfer and Messaging Application

## Overview

This project implements a simple client-server application for messaging and file transfer using TCP sockets in Python. The server can handle multiple clients, and both the server and clients have graphical user interfaces (GUIs) built with Tkinter. This project is developed as part of the CSE 3101 Computer Networking course.

## Features

- **Text Messaging**: Clients can send text messages to the server, which broadcasts them to all connected clients.
- **File Transfer**: Clients can send files to the server, which then broadcasts the file to all connected clients.
- **Acknowledgments**: The file transfer process includes acknowledgment packets to ensure reliable data transfer.
- **Timeout and Retransmission**: The server implements an Exponential Weighted Moving Average (EWMA) for timeout calculation and retransmits data packets if acknowledgments are not received within the timeout period.

## Requirements

- Python 3.x
- Tkinter (usually included with Python installations)
- Network connection

## Installation

1. Clone the repository to your local machine:
    ```sh
    git clone <https://github.com/asef-sami/Python-Chat-App.git>
    ```

2. Navigate to the project directory:
    ```sh
    cd <Python-Chat-App>
    ```

## Usage

### Running the Server

1. Start the server by running the `server.py` file:
    ```sh
    python server.py
    ```

2. The server GUI will open, allowing you to see messages from clients and send messages or files.

### Running the Client

1. Start a client by running the `client.py` file:
    ```sh
    python client.py
    ```

2. Enter your name when prompted, and the client GUI will open.

3. You can send messages to the server, which will broadcast them to all connected clients. You can also send files to the server, which will broadcast them to all connected clients.

## File Descriptions

### `server.py`

- Implements the server-side logic.
- Handles multiple clients using threads.
- Provides a GUI for server interaction.

### `client.py`

- Implements the client-side logic.
- Connects to the server and allows user interaction through a GUI.
- Handles messaging and file transfer.

## Acknowledgments

This project was inspired by the need for a simple, reliable client-server messaging and file transfer system for educational purposes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
