import tkinter as tk
import json
from ast import literal_eval as make_tuple


window = tk.Tk()
window.geometry('1500x1500')
canvas = tk.Canvas(window, height=700, width=700)
canvas.pack()

def choose_order():
    var = e.get()
    file = fe.get()
    with open(file) as f:
        data = json.load(f)
    path = data[var]["path"]
    text = data[var]["text"]
    effort = data[var]["effort"]
    t.delete('1.0',tk.END)
    t.insert('insert',text)
    t.insert('end',"\neffort\n")
    t.insert('end',effort)
    #t.insert('end',"\npath\n")
    #t.insert('end',path)
    i = 10
    canvas.delete("all")
    while (i<=700):
        j = 10
        while (j<=700):
            canvas.create_rectangle(i, j, i+10, j+10)
            j+=20
        i+=20
    points = path.split()
    for x in range(0,len(points),3):
        start = make_tuple(points[x])
        middle = make_tuple(points[x+1])
        end = make_tuple(points[x+2])
        canvas.create_rectangle(start[0]*10, start[1]*10, middle[0]*10, middle[1]*10)
        canvas.create_rectangle(middle[0]*10, middle[1]*10, end[0]*10, end[1]*10)

fe = tk.Entry(window)
fe.pack()
e = tk.Entry(window)
e.pack()
b = tk.Button(window,text="choose order",command=choose_order)
b.pack()
t = tk.Text(window)
t.pack()




window.mainloop()
