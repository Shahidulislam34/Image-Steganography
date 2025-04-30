from tkinter import *  # Imports all classes and functions from tkinter for GUI
import tkinter.filedialog  # For file browsing dialog
from tkinter import messagebox  # For showing pop-up messages
from PIL import ImageTk, Image  # For handling and displaying images
from io import BytesIO  # For in-memory image handling (not used in this code)
import os  # For interacting with the file system (not used in this code)

root = Tk()  # Create the main GUI window
root.title("Image Steganography")  # Set the title of the window

# Function to go back to the main menu
def back(frame):
    frame.destroy()  # Destroy current frame
    main()  # Reopen main menu

# Function to show the main menu
def main():
    frame = Frame(root, bg="#ffffff", bd=5)  # Create a frame in the center
    frame.place(relx=0.5, rely=0.5, anchor=CENTER)

    Label(frame, text="Image Steganography", font=("Arial", 20, "bold")).pack(pady=20)

    # Buttons to choose encode or decode
    Button(frame, text="Encode Message", font=("Arial", 14), command=lambda: encode_frame1(frame)).pack(pady=10)
    Button(frame, text="Decode Message", font=("Arial", 14), command=lambda: decode_frame1(frame)).pack(pady=10)

# UI for first encoding step
def encode_frame1(prev_frame):
    prev_frame.destroy()  # Remove previous frame
    frame1 = Frame(root, bg="#f0f0f0", bd=5)
    frame1.place(relx=0.5, rely=0.5, anchor=CENTER)

    Label(frame1, text="Select an Image to Encode", font=("Arial", 14)).pack(pady=20)
    Button(frame1, text="Browse", command=lambda: open_image(frame1, True)).pack(pady=10)
    Button(frame1, text="Back", command=lambda: back(frame1)).pack(pady=10)

# UI for first decoding step
def decode_frame1(prev_frame):
    prev_frame.destroy()
    frame1 = Frame(root, bg="#f0f0f0", bd=5)
    frame1.place(relx=0.5, rely=0.5, anchor=CENTER)

    Label(frame1, text="Select an Image to Decode", font=("Arial", 14)).pack(pady=20)
    Button(frame1, text="Browse", command=lambda: open_image(frame1, False)).pack(pady=10)
    Button(frame1, text="Back", command=lambda: back(frame1)).pack(pady=10)

# Load and display image and open next step
def open_image(frame, encode):
    path = tkinter.filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
    if path:
        img = Image.open(path)
        img = img.resize((300, 300))  # Resize image for display
        imgTk = ImageTk.PhotoImage(img)

        label = Label(frame, image=imgTk)
        label.image = imgTk  # Keep a reference to avoid garbage collection
        label.pack(pady=10)

        if encode:
            encode_frame2(frame, path)  # Continue encoding
        else:
            decode_frame2(frame, path)  # Continue decoding

# UI for encoding message into image
def encode_frame2(prev_frame, path):
    Label(prev_frame, text="Enter your secret message:", font=("Arial", 12)).pack(pady=10)
    text_area = Text(prev_frame, width=40, height=4)
    text_area.pack()

    # Function to actually encode message
    def encode_msg():
        msg = text_area.get("1.0", END).strip()
        if msg:
            enc_fun(path, msg)
            messagebox.showinfo("Success", "Message encoded and image saved as 'encoded_image.png'")
        else:
            messagebox.showerror("Error", "Please enter a message.")

    Button(prev_frame, text="Encode", command=encode_msg).pack(pady=10)

# UI for decoding message from image
def decode_frame2(prev_frame, path):
    msg = decode(Image.open(path))  # Get hidden message
    Label(prev_frame, text="Decoded Message:", font=("Arial", 12, "bold")).pack(pady=10)
    msg_area = Text(prev_frame, width=40, height=4)
    msg_area.insert(END, msg)
    msg_area.config(state=DISABLED)  # Make read-only
    msg_area.pack(pady=10)

# Convert string message to binary format
def generate_Data(data):
    new_data = []
    for i in data:
        binary = format(ord(i), '08b')  # Convert char to 8-bit binary
        new_data.append(binary)
    return new_data

# Modify pixel values to embed binary message
def modify_Pix(pix, data):
    datalist = generate_Data(data)
    lendata = len(datalist)
    imdata = iter(pix)  # Pixel data iterator

    for i in range(lendata):
        # Get next 3 pixels (9 values)
        pixels = [value for value in next(imdata)[:3] +
                                  next(imdata)[:3] +
                                  next(imdata)[:3]]
        # Modify the first 8 pixels for message bits
        for j in range(0, 8):
            if datalist[i][j] == '0' and pixels[j] % 2 != 0:
                pixels[j] -= 1
            elif datalist[i][j] == '1' and pixels[j] % 2 == 0:
                if pixels[j] != 0:
                    pixels[j] -= 1
                else:
                    pixels[j] += 1

        # Use 9th pixel as end marker
        if i == lendata - 1:
            if pixels[-1] % 2 == 0:
                if pixels[-1] != 0:
                    pixels[-1] -= 1
                else:
                    pixels[-1] += 1
        else:
            if pixels[-1] % 2 != 0:
                pixels[-1] -= 1

        # Return the modified pixels
        yield tuple(pixels[0:3])
        yield tuple(pixels[3:6])
        yield tuple(pixels[6:9])

# Put modified pixels back into a new image
def encode_enc(img, data):
    newimg = img.copy()
    w = newimg.size[0]
    (x, y) = (0, 0)

    for pixel in modify_Pix(img.getdata(), data):
        newimg.putpixel((x, y), pixel)
        if x == w - 1:
            x = 0
            y += 1
        else:
            x += 1

    newimg.save("encoded_image.png")  # Save the stego-image

# Helper to open image, encode message, and mark the end with '#####'
def enc_fun(path, message):
    img = Image.open(path)
    data = message + '#####'  # End-of-message marker
    encode_enc(img, data)

# Read pixel data and decode message
def decode(img):
    data = ''
    imgdata = iter(img.getdata())
    while True:
        # Get next 3 pixels = 9 values
        pixels = [value for value in next(imgdata)[:3] +
                              next(imgdata)[:3] +
                              next(imgdata)[:3]]
        binary_str = ''
        for i in pixels[:8]:  # Read 8 bits
            binary_str += '1' if i % 2 else '0'
        char = chr(int(binary_str, 2))  # Convert binary to character
        data += char
        if data[-5:] == '#####':  # Stop if end marker is found
            break
    return data[:-5]  # Remove the end marker and return message

main()  # Launch the main GUI
root.geometry("500x500")  # Set window size
root.mainloop()  # Run the GUI event loop
