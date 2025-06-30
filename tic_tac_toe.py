import tkinter as tk
from tkinter import messagebox
import random

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.resizable(False, False)
        
        self.current_player = "X"
        self.board = [""] * 9
        self.game_over = False
        
        # Create menu
        self.menu = tk.Menu(root)
        self.root.config(menu=self.menu)
        
        self.game_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Game", menu=self.game_menu)
        self.game_menu.add_command(label="New Game", command=self.reset_game)
        self.game_menu.add_separator()
        self.game_menu.add_command(label="Exit", command=root.quit)
        
        # Create game mode selection
        self.mode_frame = tk.Frame(root)
        self.mode_frame.pack(pady=10)
        
        self.mode_label = tk.Label(self.mode_frame, text="Select Game Mode:")
        self.mode_label.grid(row=0, column=0, padx=5)
        
        self.mode_var = tk.StringVar(value="pvp")
        self.pvp_radio = tk.Radiobutton(self.mode_frame, text="Player vs Player", variable=self.mode_var, value="pvp")
        self.pvc_radio = tk.Radiobutton(self.mode_frame, text="Player vs Computer", variable=self.mode_var, value="pvc")
        
        self.pvp_radio.grid(row=0, column=1, padx=5)
        self.pvc_radio.grid(row=0, column=2, padx=5)
        
        # Status label
        self.status_label = tk.Label(root, text="Player X's turn", font=("Arial", 12))
        self.status_label.pack(pady=5)
        
        # Game board
        self.board_frame = tk.Frame(root)
        self.board_frame.pack()
        
        self.buttons = []
        for i in range(3):
            for j in range(3):
                button = tk.Button(self.board_frame, text="", font=("Arial", 24, "bold"), 
                                  width=5, height=2, 
                                  command=lambda row=i, col=j: self.make_move(row, col))
                button.grid(row=i, column=j, padx=2, pady=2)
                self.buttons.append(button)
    
    def make_move(self, row, col):
        index = row * 3 + col
        
        if self.board[index] == "" and not self.game_over:
            self.board[index] = self.current_player
            self.buttons[index].config(text=self.current_player)
            
            if self.current_player == "X":
                self.buttons[index].config(fg="blue")
            else:
                self.buttons[index].config(fg="red")
            
            if self.check_winner():
                self.status_label.config(text=f"Player {self.current_player} wins!")
                self.game_over = True
                messagebox.showinfo("Game Over", f"Player {self.current_player} wins!")
            elif "" not in self.board:
                self.status_label.config(text="It's a tie!")
                self.game_over = True
                messagebox.showinfo("Game Over", "It's a tie!")
            else:
                self.current_player = "O" if self.current_player == "X" else "X"
                self.status_label.config(text=f"Player {self.current_player}'s turn")
                
                # If playing against computer and it's O's turn
                if self.mode_var.get() == "pvc" and self.current_player == "O" and not self.game_over:
                    self.root.after(500, self.computer_move)
    
    def computer_move(self):
        # Simple AI: first try to win, then block player, then random move
        
        # Check for winning move
        for i in range(9):
            if self.board[i] == "":
                self.board[i] = "O"
                if self.check_winner(False):
                    self.buttons[i].config(text="O", fg="red")
                    self.status_label.config(text="Computer wins!")
                    self.game_over = True
                    messagebox.showinfo("Game Over", "Computer wins!")
                    return
                self.board[i] = ""
        
        # Check for blocking move
        for i in range(9):
            if self.board[i] == "":
                self.board[i] = "X"
                if self.check_winner(False):
                    self.board[i] = "O"
                    self.buttons[i].config(text="O", fg="red")
                    self.current_player = "X"
                    self.status_label.config(text="Player X's turn")
                    return
                self.board[i] = ""
        
        # Random move
        empty_cells = [i for i, val in enumerate(self.board) if val == ""]
        if empty_cells:
            index = random.choice(empty_cells)
            self.board[index] = "O"
            self.buttons[index].config(text="O", fg="red")
            
            if self.check_winner():
                self.status_label.config(text="Computer wins!")
                self.game_over = True
                messagebox.showinfo("Game Over", "Computer wins!")
            elif "" not in self.board:
                self.status_label.config(text="It's a tie!")
                self.game_over = True
                messagebox.showinfo("Game Over", "It's a tie!")
            else:
                self.current_player = "X"
                self.status_label.config(text="Player X's turn")
    
    def check_winner(self, update=True):
        # Check rows
        for i in range(0, 9, 3):
            if self.board[i] == self.board[i+1] == self.board[i+2] != "":
                if update:
                    self.highlight_winning_line([i, i+1, i+2])
                return True
        
        # Check columns
        for i in range(3):
            if self.board[i] == self.board[i+3] == self.board[i+6] != "":
                if update:
                    self.highlight_winning_line([i, i+3, i+6])
                return True
        
        # Check diagonals
        if self.board[0] == self.board[4] == self.board[8] != "":
            if update:
                self.highlight_winning_line([0, 4, 8])
            return True
        if self.board[2] == self.board[4] == self.board[6] != "":
            if update:
                self.highlight_winning_line([2, 4, 6])
            return True
        
        return False
    
    def highlight_winning_line(self, indices):
        for i in indices:
            self.buttons[i].config(bg="light green")
    
    def reset_game(self):
        self.current_player = "X"
        self.board = [""] * 9
        self.game_over = False
        self.status_label.config(text="Player X's turn")
        
        for button in self.buttons:
            button.config(text="", bg="SystemButtonFace", fg="black")

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()