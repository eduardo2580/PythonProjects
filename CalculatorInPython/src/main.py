import tkinter as tk

def clear_input():
    """Clear the display."""
    display.delete(0, tk.END)

def delete_char():
    """Delete the last character from the display."""
    current = display.get()
    display.delete(0, tk.END)
    display.insert(0, current[:-1])

def append_char(char):
    """Append a character to the display."""
    display.insert(tk.END, char)

def calculate():
    """Evaluate the expression in the display."""
    try:
        expression = display.get()
        result = eval(expression)
        display.delete(0, tk.END)
        display.insert(0, str(result))
    except:
        display.delete(0, tk.END)
        display.insert(0, "Error")

# Create the main window
window = tk.Tk()
window.title("Calculator")

# Create the display
display = tk.Entry(window, font=('Arial', 24), justify='right')
display.grid(row=0, column=0, columnspan=4, sticky='nsew', padx=5, pady=5)

# Define buttons
buttons = [
    ('C', 1, 0), ('DEL', 1, 1), ('%', 1, 2), ('/', 1, 3),
    ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('*', 2, 3),
    ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('-', 3, 3),
    ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('+', 4, 3),
    ('0', 5, 0), ('.', 5, 1), ('=', 5, 2)
]

# Create and place buttons
for (text, row, col) in buttons:
    if text == '=':
        btn = tk.Button(window, text=text, command=calculate)
        btn.grid(row=row, column=col, columnspan=2, sticky='nsew', padx=2, pady=2)
    else:
        if text == 'C':
            btn = tk.Button(window, text=text, command=clear_input)
        elif text == 'DEL':
            btn = tk.Button(window, text=text, command=delete_char)
        else:
            btn = tk.Button(window, text=text, command=lambda char=text: append_char(char))
        btn.grid(row=row, column=col, sticky='nsew', padx=2, pady=2)

# Configure grid weights
for i in range(6):
    window.rowconfigure(i, weight=1)
for j in range(4):
    window.columnconfigure(j, weight=1)

window.mainloop()