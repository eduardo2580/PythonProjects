import tkinter

def set_tile(row, column):
    global curr_player

    if (game_over):
        return

    if board[row][column]["text"] != "":
        return
    
    board[row][column]["text"] = curr_player

    if curr_player == playerO:
        curr_player = playerX
    else:
        curr_player = playerO
    
    turn_label["text"] = curr_player+"'s turn"

    check_winner()

def check_winner():
    global turns, game_over, scoreX, scoreO
    turns += 1

    for row in range(3):
        if (board[row][0]["text"] == board[row][1]["text"] == board[row][2]["text"]
            and board[row][0]["text"] != ""):
            winner = board[row][0]["text"]
            turn_label.config(text=winner+" is the winner!", foreground=color_yellow)
            for column in range(3):
                board[row][column].config(foreground=color_yellow, background=color_light_gray)
            game_over = True
            update_score(winner)
            return
    
    for column in range(3):
        if (board[0][column]["text"] == board[1][column]["text"] == board[2][column]["text"]
            and board[0][column]["text"] != ""):
            winner = board[0][column]["text"]
            turn_label.config(text=winner+" is the winner!", foreground=color_yellow)
            for row in range(3):
                board[row][column].config(foreground=color_yellow, background=color_light_gray)
            game_over = True
            update_score(winner)
            return
    
    if (board[0][0]["text"] == board[1][1]["text"] == board[2][2]["text"]
        and board[0][0]["text"] != ""):
        winner = board[0][0]["text"]
        turn_label.config(text=winner+" is the winner!", foreground=color_yellow)
        for i in range(3):
            board[i][i].config(foreground=color_yellow, background=color_light_gray)
        game_over = True
        update_score(winner)
        return

    if (board[0][2]["text"] == board[1][1]["text"] == board[2][0]["text"]
        and board[0][2]["text"] != ""):
        winner = board[0][2]["text"]
        turn_label.config(text=winner+" is the winner!", foreground=color_yellow)
        board[0][2].config(foreground=color_yellow, background=color_light_gray)
        board[1][1].config(foreground=color_yellow, background=color_light_gray)
        board[2][0].config(foreground=color_yellow, background=color_light_gray)
        game_over = True
        update_score(winner)
        return
    
    if (turns == 9):
        game_over = True
        turn_label.config(text="Tie!", foreground=color_yellow)

def update_score(winner):
    global scoreX, scoreO
    if winner == playerX:
        scoreX += 1
    else:
        scoreO += 1
    score_label.config(text=f"X: {scoreX}  |  O: {scoreO}")

def new_game():
    global turns, game_over, curr_player

    turns = 0
    game_over = False
    curr_player = playerX

    turn_label.config(text=curr_player+"'s turn", foreground="white")

    for row in range(3):
        for column in range(3):
            board[row][column].config(text="", foreground=color_blue, background=color_gray)

# Game setup
playerX = "X"
playerO = "O"
curr_player = playerX
board = [[0, 0, 0], 
         [0, 0, 0], 
         [0, 0, 0]]

scoreX = 0
scoreO = 0

color_blue = "#4584b6"
color_yellow = "#ffde57"
color_gray = "#343434"
color_light_gray = "#646464"
color_dark_bg = "#1e1e1e"

turns = 0
game_over = False

# Window setup
window = tkinter.Tk()
window.title("Tic Tac Toe")
window.resizable(False, False)
window.configure(background=color_dark_bg)

frame = tkinter.Frame(window, background=color_dark_bg)

score_label = tkinter.Label(frame, text=f"X: {scoreX}  |  O: {scoreO}", font=("Consolas", 16, "bold"), 
                            background=color_dark_bg, foreground=color_yellow)
score_label.grid(row=0, column=0, columnspan=3, sticky="we", pady=10)

turn_label = tkinter.Label(frame, text=curr_player+"'s turn", font=("Consolas", 20, "bold"), 
                           background=color_gray, foreground="white")
turn_label.grid(row=1, column=0, columnspan=3, sticky="we")

for row in range(3):
    for column in range(3):
        board[row][column] = tkinter.Button(frame, text="", font=("Consolas", 50, "bold"),
                                            background=color_gray, foreground=color_blue, width=4, height=1,
                                            command=lambda row=row, column=column: set_tile(row, column))
        board[row][column].grid(row=row+2, column=column, padx=2, pady=2)

button = tkinter.Button(frame, text="restart", font=("Consolas", 20, "bold"), background=color_gray,
                        foreground=color_yellow, command=new_game)
button.grid(row=5, column=0, columnspan=3, sticky="we", pady=10)

frame.pack(padx=10, pady=10)

# Center the window
window.update()
window_width = window.winfo_width()
window_height = window.winfo_height()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

window_x = int((screen_width/2) - (window_width/2))
window_y = int((screen_height/2) - (window_height/2))

window.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

window.mainloop()