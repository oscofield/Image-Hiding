from tkinter import *
from tkinter import filedialog, messagebox
import tkinter as tk
from PIL import Image, ImageTk
import os

filename = None
secret = None

def genData(data):
    newd = []
    for i in data:
        newd.append(format(ord(i), '08b'))
    return newd

def modPix(pix, data):
    datalist = genData(data)
    lendata = len(datalist)
    imdata = iter(pix)
    for i in range(lendata):
        pix = [value for value in imdata.__next__()[:3] +
                                imdata.__next__()[:3] +
                                imdata.__next__()[:3]]
        for j in range(8):
            if (datalist[i][j] == '0' and pix[j] % 2 != 0):
                pix[j] -= 1
            elif (datalist[i][j] == '1' and pix[j] % 2 == 0):
                if pix[j] != 0:
                    pix[j] -= 1
                else:
                    pix[j] += 1
        if (i == lendata - 1):
            if (pix[-1] % 2 == 0):
                if pix[-1] != 0:
                    pix[-1] -= 1
                else:
                    pix[-1] += 1
        else:
            if (pix[-1] % 2 != 0):
                pix[-1] -= 1
        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]

def encode_enc(newimg, data):
    w = newimg.size[0]
    (x, y) = (0, 0)
    for pixel in modPix(newimg.getdata(), data):
        newimg.putpixel((x, y), pixel)
        if (x == w - 1):
            x = 0
            y += 1
        else:
            x += 1

def encode(image, data):
    newimg = image.copy()
    encode_enc(newimg, data)
    return newimg

def decode(image):
    data = ''
    imgdata = iter(image.getdata())
    while True:
        pixels = [value for value in imgdata.__next__()[:3] +
                                    imgdata.__next__()[:3] +
                                    imgdata.__next__()[:3]]
        binstr = ''
        for i in pixels[:8]:
            if i % 2 == 0:
                binstr += '0'
            else:
                binstr += '1'
        data += chr(int(binstr, 2))
        if pixels[-1] % 2 != 0:
            return data

def showimage():
    global filename
    filename = filedialog.askopenfilename(initialdir=os.getcwd(),
                                          title='Select Image File',
                                          filetypes=(("PNG file", "*.png"),
                                                     ("JPG file", "*.jpg"),
                                                     ("All files", "*.*")))
    if filename:
        img = Image.open(filename)
        img.thumbnail((400, 400))  
        img = ImageTk.PhotoImage(img)
        lbl.configure(image=img)
        lbl.image = img

def Hide():
    global secret, filename
    if not filename:
        messagebox.showerror("Error", "Please select an image first.")
        return
    message = text1.get(1.0, END).strip()
    if not message:
        messagebox.showerror("Error", "Please enter a message to hide.")
        return
    image = Image.open(filename)
    secret = encode(image, message)
    messagebox.showinfo("Success", "Message hidden successfully.")

def Show():
    global filename
    if not filename:
        messagebox.showerror("Error", "Please select an image first.")
        return
    image = Image.open(filename)
    try:
        clear_message = decode(image)
        text1.delete(1.0, END)
        text1.insert(END, clear_message)
    except Exception as e:
        messagebox.showerror("Error", "Failed to decode message. The image may not contain a hidden message.")

def save():
    global secret
    if secret is None:
        messagebox.showerror("Error", "No hidden message to save. Please hide a message first.")
        return
    save_path = save_location_entry.get()
    save_name = save_name_entry.get()
    if not save_path:
        save_path = os.getcwd()
    if not os.path.exists(save_path):
        messagebox.showerror("Error", "The specified save path does not exist.")
        return
    if not save_name:
        save_name = "hidden.png"
    elif not save_name.lower().endswith(('.png', '.jpg', '.jpeg')):
        save_name += '.png'
    
    full_path = os.path.join(save_path, save_name)
    secret.save(full_path)
    messagebox.showinfo("Success", f"Image saved as {full_path}")
    reset()

def browse_save_location():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        save_location_entry.delete(0, END)
        save_location_entry.insert(0, folder_selected)

def reset():
    global filename, secret
    filename = None
    secret = None
    lbl.configure(image='')
    text1.delete(1.0, END)
    save_location_entry.delete(0, END)
    save_name_entry.delete(0, END)
    messagebox.showinfo("Reset", "All fields have been reset.")

# GUI setup
root = Tk()
root.title("Steganography - Hide Secret Messages in Images")
root.geometry("1000x700+150+50")
root.resizable(False, False)
root.configure(bg="#1e1e1e")

# Color scheme
primary_color = "#007acc"
secondary_color = "#252526"
text_color = "#ffffff"
button_color = "#0e639c"
button_text_color = "#ffffff"

# GUI elements
title_frame = Frame(root, bg=primary_color, height=60)
title_frame.pack(fill=X)

title_label = Label(title_frame, text="IMAGE STEGANOGRAPHY", bg=primary_color, fg=text_color, font="Helvetica 24 bold")
title_label.pack(pady=10)

main_frame = Frame(root, bg="#1e1e1e")
main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

# Image display area
image_frame = Frame(main_frame, bg=secondary_color, width=450, height=450)
image_frame.pack(side=LEFT, padx=(0, 10))

lbl = Label(image_frame, bg=secondary_color)
lbl.place(relwidth=1, relheight=1)

# Text input/output area
text_frame = Frame(main_frame, bg=secondary_color, width=450, height=450)
text_frame.pack(side=LEFT, padx=(10, 0))

text1 = Text(text_frame, font="Roboto 14", bg=secondary_color, fg=text_color, relief=FLAT, padx=10, pady=10)
text1.place(relwidth=1, relheight=1)

scrollbar = Scrollbar(text_frame)
scrollbar.place(relx=1, rely=0, relheight=1, anchor='ne')
scrollbar.configure(command=text1.yview)
text1.configure(yscrollcommand=scrollbar.set)

# Button area
button_frame = Frame(root, bg="#1e1e1e", height=100)
button_frame.pack(fill=X, padx=20, pady=20)

button_style = {"font": "Helvetica 12 bold", "fg": button_text_color, "width": 15, "height": 2, "bd": 0}
browse_button_style = {"font": "Helvetica 12 bold", "fg": button_text_color, "width": 10, "height": 1, "bd": 0}

Button(button_frame, text="Open Image", command=showimage, bg=button_color, **button_style).pack(side=LEFT, padx=5)
Button(button_frame, text="Hide Data", command=Hide, bg=button_color, **button_style).pack(side=LEFT, padx=5)
Button(button_frame, text="Show Data", command=Show, bg=button_color, **button_style).pack(side=LEFT, padx=5)
Button(button_frame, text="Save Image", command=save, bg=button_color, **button_style).pack(side=LEFT, padx=5)
Button(button_frame, text="Reset", command=reset, bg="#d64045", **button_style).pack(side=LEFT, padx=5)

# Save options area
save_frame = Frame(root, bg=secondary_color, height=80)
save_frame.pack(fill=X, padx=20, pady=(0, 20))

Label(save_frame, text="Save Location:", bg=secondary_color, fg=text_color, font="Helvetica 12").grid(row=0, column=0, padx=10, pady=5, sticky='w')
save_location_entry = Entry(save_frame, width=50, font="Helvetica 12", bg="#3c3c3c", fg=text_color, bd=0)
save_location_entry.grid(row=0, column=1, padx=10, pady=5)
Button(save_frame, text="Browse", command=browse_save_location, bg=button_color, **browse_button_style).grid(row=0, column=2, padx=10, pady=5)

Label(save_frame, text="Save Name:", bg=secondary_color, fg=text_color, font="Helvetica 12").grid(row=1, column=0, padx=10, pady=5, sticky='w')
save_name_entry = Entry(save_frame, width=50, font="Helvetica 12", bg="#3c3c3c", fg=text_color, bd=0)
save_name_entry.grid(row=1, column=1, padx=10, pady=5)

root.mainloop()