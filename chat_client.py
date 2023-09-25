import socket 
from threading import Thread
import curses
import multiprocessing

HEADER_LEN = 10
IP = "127.0.0.1"
PORT = 1234

class Client:
    def __init__(self):
        # NETWORKING
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((IP, PORT))
        self.s.settimeout(.3)
        self.stop = False

        # GUI
        self.stdscr = curses.initscr()
        curses.start_color()
        self.rows, self.cols = self.stdscr.getmaxyx()
        self.chat_window = curses.newwin(self.rows-3,self.cols,0,0)
        self.chat_window.scrollok(True)

        # Color pairs
        curses.init_pair(1,curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2,curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3,curses.COLOR_CYAN, curses.COLOR_BLACK)
        self.GREEN = curses.color_pair(1)
        self.RED = curses.color_pair(2)
        self.CYAN = curses.color_pair(3)
        self.cur_row = 0
        self.cur_col = 0
        self.username = ""

    """
    NETWORKING METHODS
    """
    def format_msg(self,msg):
        return bytes(f"{len(msg):<{HEADER_LEN}}" + msg,'utf-8')

    def read_header(self):
        header = self.s.recv(HEADER_LEN)
        if len(header) > 0:
            return int(header)
        else:
            return -1
    

    def send_msg(self,msg):
        try:
            self.s.send(self.format_msg(msg))
        except:
            print("ERROR")

    def read_from_server(self):
        while True:
            if self.stop:
                    break
            try:
                header = self.read_header()
                if header != -1:
                    msg = self.s.recv(header).decode('utf-8')
                    self.write_to_terminal(msg)
                
            except Exception as e:
                # self.stdscr.addstr(20,20,str(e))
                # self.stdscr.refresh()
                pass
    """
    GUI METHODS
    """
    def get_row_col(self):
        rows, cols = self.stdscr.getmaxyx()
        return rows-2, 1

    def read(self, cols):
        y,x = self.stdscr.getyx()
        msg = self.stdscr.getstr(y,x,cols)
        return msg.decode('utf-8')

    def write_to_terminal(self, msg):
        CURSOR_ROW, CURSOR_COL = self.get_row_col()

        self.chat_window.addstr(self.cur_row, self.cur_col, msg)
        self.chat_window.refresh()
        self.cur_row += 1
        self.reset_prompt(CURSOR_ROW, CURSOR_COL)
        

    def reset_prompt(self,row, col):
        self.stdscr.move(row, col)
        self.stdscr.clrtoeol()
        self.stdscr.move(row, col)
        self.stdscr.addstr(f"{self.username} -> ",self.GREEN)


    """
    MAIN 
    """
    def start_client(self):
        CURSOR_ROW, CURSOR_COL = self.get_row_col()
        
        self.stdscr.addstr(1,0,"Enter your username: ")
        self.username = self.read(self.cols)

        self.stdscr.clear()
        self.stdscr.addstr(self.rows-3,1,f"-"*(int(self.cols/8)),self.GREEN)
        self.reset_prompt(CURSOR_ROW, CURSOR_COL)

        self.stdscr.refresh()
        self.stdscr.scrollok(True)

        # Send username to server
        self.send_msg(self.username)

        # Start revieving data from server
        #recieve = multiprocessing.Process(target=self.read_from_server, args=())
        recieve = Thread(target=self.read_from_server)
        recieve.start()

        while True:
            # Update terminal
            curses.echo()
            msg = self.read(self.cols)
            if len(msg) > 0:
                if msg == ":exit":
                    break
                self.write_to_terminal(f"{self.username}: {msg}")
                self.send_msg(f"{self.username}: {msg}")
            
        self.stop = True
        print("EXITING")
        curses.endwin()
        recieve.join()
            
        
client = Client()
client.start_client()
