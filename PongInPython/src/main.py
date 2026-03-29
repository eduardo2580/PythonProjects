import turtle
import time
import random
import sys

# Screen setup
wn = turtle.Screen()
wn.title("Ultimate Pong")
wn.bgcolor("black")
wn.setup(width=800, height=600)
wn.tracer(0)

# Constants
PADDLE_WIDTH = 1
PADDLE_HEIGHT = 5
BALL_SPEED_X = 2.00
BALL_SPEED_Y = 2.00
PADDLE_SPEED = 20
WINNING_SCORE = 5

# Colors
WHITE = "white"
BLACK = "black"

# Game state variables
score_a = 0
score_b = 0
game_state = "menu"  # menu, playing, paused, game_over

# Create reusable turtle for text
text_turtle = turtle.Turtle()
text_turtle.hideturtle()
text_turtle.penup()
text_turtle.color(WHITE)

# Paddle A
paddle_a = turtle.Turtle()
paddle_a.speed(0)
paddle_a.shape("square")
paddle_a.color(WHITE)
paddle_a.shapesize(stretch_wid=PADDLE_HEIGHT, stretch_len=PADDLE_WIDTH)
paddle_a.penup()
paddle_a.goto(-350, 0)

# Paddle B
paddle_b = turtle.Turtle()
paddle_b.speed(0)
paddle_b.shape("square")
paddle_b.color(WHITE)
paddle_b.shapesize(stretch_wid=PADDLE_HEIGHT, stretch_len=PADDLE_WIDTH)
paddle_b.penup()
paddle_b.goto(350, 0)

# Ball
ball = turtle.Turtle()
ball.speed(0)
ball.shape("square")
ball.color(WHITE)
ball.penup()
ball.goto(0, 0)
ball.dx = BALL_SPEED_X
ball.dy = BALL_SPEED_Y

# Center Line
center_line = turtle.Turtle()
center_line.speed(0)
center_line.color(WHITE)
center_line.penup()
center_line.goto(0, 300)
center_line.pendown()
center_line.goto(0, -300)
center_line.hideturtle()

# Score Display
pen = turtle.Turtle()
pen.speed(0)
pen.color(WHITE)
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Player A: 0  Player B: 0", align="center", font=("Courier", 24, "normal"))

def paddle_a_up():
    y = paddle_a.ycor()
    if y < 250:
        y += PADDLE_SPEED
        paddle_a.sety(y)

def paddle_a_down():
    y = paddle_a.ycor()
    if y > -250:
        y -= PADDLE_SPEED
        paddle_a.sety(y)

def paddle_b_up():
    y = paddle_b.ycor()
    if y < 250:
        y += PADDLE_SPEED
        paddle_b.sety(y)

def paddle_b_down():
    y = paddle_b.ycor()
    if y > -250:
        y -= PADDLE_SPEED
        paddle_b.sety(y)

def reset_ball():
    ball.goto(0, 0)
    ball.dx = BALL_SPEED_X * random.choice([-1, 1])
    ball.dy = BALL_SPEED_Y * random.choice([-1, 1])

def update_score():
    pen.clear()
    pen.write(f"Player A: {score_a}  Player B: {score_b}", align="center", font=("Courier", 24, "normal"))

def show_winner(winner):
    text_turtle.clear()
    text_turtle.goto(0, 0)
    text_turtle.write(f"{winner} Wins!", align="center", font=("Courier", 36, "normal"))
    time.sleep(2)
    text_turtle.clear()

def show_countdown():
    for i in range(3, 0, -1):
        text_turtle.clear()
        text_turtle.goto(0, 0)
        text_turtle.write(f"{i}", align="center", font=("Courier", 36, "normal"))
        wn.update()
        time.sleep(1)
    text_turtle.clear()

def toggle_pause():
    global game_state
    if game_state == "playing":
        game_state = "paused"
        text_turtle.clear()
        text_turtle.goto(0, 0)
        text_turtle.write("PAUSED", align="center", font=("Courier", 36, "normal"))
    elif game_state == "paused":
        game_state = "playing"
        text_turtle.clear()

def draw_menu():
    text_turtle.clear()
    text_turtle.goto(0, 100)
    text_turtle.write("ULTIMATE PONG", align="center", font=("Courier", 40, "normal"))
    text_turtle.goto(0, 0)
    text_turtle.write("Press ENTER or SPACE to Start", align="center", font=("Courier", 24, "normal"))
    text_turtle.goto(0, -50)
    text_turtle.write("Controls:", align="center", font=("Courier", 20, "normal"))
    text_turtle.goto(0, -90)
    text_turtle.write("Player A: W/S", align="center", font=("Courier", 16, "normal"))
    text_turtle.goto(0, -120)
    text_turtle.write("Player B: Up/Down Arrows", align="center", font=("Courier", 16, "normal"))
    text_turtle.goto(0, -160)
    text_turtle.write("P: Pause   Space: Start / Reset Ball", align="center", font=("Courier", 16, "normal"))

def start_game():
    global game_state, score_a, score_b
    score_a = 0
    score_b = 0
    reset_ball()
    paddle_a.goto(-350, 0)
    paddle_b.goto(350, 0)
    update_score()
    show_countdown()
    game_state = "playing"

def start_game_from_menu():
    global game_state
    if game_state == "menu":
        start_game()

def space_action():
    global game_state
    if game_state == "menu":
        start_game()
    elif game_state == "playing":
        reset_ball()

def handle_key_press():
    wn.listen()
    wn.onkeypress(paddle_a_up, "w")
    wn.onkeypress(paddle_a_down, "s")
    wn.onkeypress(paddle_b_up, "Up")
    wn.onkeypress(paddle_b_down, "Down")
    wn.onkeypress(toggle_pause, "p")
    wn.onkeypress(start_game_from_menu, "Return")
    wn.onkeypress(space_action, "space")
    wn.onkeypress(lambda: sys.exit(), "Escape")

def game_loop():
    global score_a, score_b, game_state

    if game_state == "playing":
        # Move the ball
        ball.setx(ball.xcor() + ball.dx)
        ball.sety(ball.ycor() + ball.dy)

        # Border collisions
        if ball.ycor() > 290:
            ball.sety(290)
            ball.dy *= -1
        elif ball.ycor() < -290:
            ball.sety(-290)
            ball.dy *= -1

        # Scoring
        if ball.xcor() > 390:
            score_a += 1
            update_score()
            reset_ball()
            if score_a >= WINNING_SCORE:
                show_winner("Player A")
                game_state = "menu"
                score_a = score_b = 0
                update_score()
        elif ball.xcor() < -390:
            score_b += 1
            update_score()
            reset_ball()
            if score_b >= WINNING_SCORE:
                show_winner("Player B")
                game_state = "menu"
                score_a = score_b = 0
                update_score()

        # Paddle collisions
        if (ball.xcor() < -340 and ball.ycor() < paddle_a.ycor() + 50 and ball.ycor() > paddle_a.ycor() - 50):
            ball.setx(-340)
            ball.dx *= -1
        elif (ball.xcor() > 340 and ball.ycor() < paddle_b.ycor() + 50 and ball.ycor() > paddle_b.ycor() - 50):
            ball.setx(340)
            ball.dx *= -1

        # Paddle boundaries
        for paddle in [paddle_a, paddle_b]:
            if paddle.ycor() > 250:
                paddle.sety(250)
            elif paddle.ycor() < -250:
                paddle.sety(-250)

    elif game_state == "menu":
        draw_menu()

    wn.update()
    wn.ontimer(game_loop, 10)

# Set up keyboard handling
handle_key_press()

# Start the game loop
game_loop()
wn.mainloop()