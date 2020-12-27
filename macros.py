import pynput
from pynput.keyboard import Key, Listener, Controller
import pyperclip
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from threading import Thread
import pickle
import re


### FIX VENV !

snippets = [
    {'code':'', 'value':''},
]

### DEBUG
logging=True
def log(message):
    if logging is True:
        print(message)

## Magic key
magic_key = Key.ctrl_r

## Key presses
keyboard = Controller()

def typer(char):
    keyboard.press(char)
    keyboard.release(char)



# DB
def pickle_out(file_name):
    """Exports buttons snippets to .pkl file"""
    with open(f"{file_name}", "wb") as output:
        pickle.dump(snippets, output, pickle.HIGHEST_PROTOCOL)


def pickle_in(file_name):
    """imports and overwrittes snippets list with content from .pkl file"""
    with open(file_name, "rb") as in_put:
        global snippets
        snippets = pickle.load(in_put)


### Snippet_assist
def snippet_tool(code):
    for s in snippets:
        if s['code'] == code:
            snip = s
            log(f"{snip} loded")
            #  get code count
            backspace_count = len(s['code'])
            # delete code
            for i in range(backspace_count):
                typer(Key.backspace)
            # insert snippet
            for char in s['value']:
                typer(char)
            break


###   KEY LISTENER   ###
magic_count = 0
code_mode = False
code = ""


def on_release(key):
    global magic_count
    global code_mode
    global code_mode_indicator

    if code_mode:
        global code
        if key == magic_key:
            # do the thing
            snippet_tool(code)
            log("Snippet deployed!!")
            # set code_mode back to False
            code_mode = False
            code = ""
            code_mode_indicator.config(bg="red")
            log("Code Mode Off")
            current_code_indicator['text'] = ""

        else:
            # enable changing/deleting code
            if key == Key.backspace:
                code = code[0:-1]
            else:
                try:
                    k = str(key.char)
                except:
                    return
                code = code + k
            log("Current code: {}".format(code))
            current_code_indicator['text'] = code
    elif key == magic_key:
        magic_count += 1
        if magic_count == 2:
            code_mode = True
            code_mode_indicator.config(bg="green")
            log("Code Mode On")
            # reset magic_count for a new round
            magic_count = 0
    else:
        magic_count = 0


def key_listener():
    with Listener(on_release=on_release) as listener:
        listener.join()


thread_listener = Thread(target=key_listener)
thread_listener.start()

## GUI ##
def update_snippets_menu():
    menu = menu_snippets['menu']
    menu.delete(0,tk.END)
    for snip in snippets:
        menu.add_command(label=snip['code'], command=lambda value = snip['code']: var_snippets_menu.set(value))
        try:
            var_snippets_menu.set(snippets[0]['code'])
        except Exception as e:
            var_snippets_menu.set("Add new first")


def command_always_on_top():
    if var_always_on_top.get() == 1:
        root.wm_attributes("-topmost", 1)
    else:
        root.wm_attributes("-topmost", 0)


def command_add_new():
    code = entry_new_code.get()
    if code == "":
        messagebox.showinfo("Failed to create a new Snippet", "You must provide a unique code")
        return
    elif code in [snip['code'] for snip in snippets]:
        messagebox.showinfo("Failed to create a new Snippet", "Code '{}' already in use!".format(code))
        return
    value = entry_new_value.get()
    snippets.append({"code":code, "value":value})
    # updating things
    entry_new_code.delete(0, tk.END)
    entry_new_value.delete(0, tk.END)
    update_snippets_menu()

def command_import():
    import_filename = filedialog.askopenfilename(initialdir = "./",title = "Select file",filetypes = (("pkl files","*.pkl"),("all files","*.*")))
    if import_filename == "":
        return
    pickle_in(import_filename)
    update_snippets_menu()

def command_export():
    file_name = filedialog.asksaveasfilename(initialdir = "./", title = "Select file",filetypes = (("pkl files","*.pkl"),("all files","*.*")))
    if file_name != "":
        file_name = file_name + '.pkl'
        pickle_out(file_name)


def command_delete_button():
    # remove dict in buttons list
    global snippets
    snippets = [snip for snip in snippets if snip['code'] != var_snippets_menu.get()]
    # remove button
    update_snippets_menu()


first_loop = True
root = tk.Tk()
root.title("Macros 1.0")
# main frame
main_frame = tk.Frame(root)
main_frame.grid(row=0, column=0)
# mode indicator
code_mode_indicator = tk.Label(main_frame, bg="red", text="Code Mode")
code_mode_indicator.grid(row=0, column=0)
# code indicator
current_code_indicator = tk.Label(main_frame, width=8)
current_code_indicator.grid(row=0, column=1)
# Import / Export
button_import = tk.Button(main_frame, text="Import", command=command_import, relief=tk.GROOVE)
button_import.grid(column=2, row=0, padx=2)
button_export = tk.Button(main_frame, text="Export", command=command_export, relief=tk.GROOVE)
button_export.grid(column=3, row=0, padx=2)
# Always on top
var_always_on_top = tk.IntVar()
ckbox_always_on_top = tk.Checkbutton(main_frame, text="Top", variable=var_always_on_top, command=command_always_on_top)
ckbox_always_on_top.grid(row=0, column=4, sticky='e')

# menu
var_snippets_menu = tk.StringVar(main_frame)
var_snippets_menu.set(snippets[0]['code'])
menu_snippets = tk.OptionMenu(main_frame, var_snippets_menu, *[snip['code'] for snip in snippets])
menu_snippets.grid(column=0, row=1, padx=2, sticky='w')
# delete from menu
button_delete_button = tk.Button(main_frame, text="Delete", command=command_delete_button, relief=tk.GROOVE)
button_delete_button.grid(column=1, row=1, padx=2, sticky='w')

# Add new snippet
label_add_new_code = tk.Label(main_frame, text="Code")
label_add_new_code.grid(column=0, row=2)
entry_new_code = tk.Entry(main_frame)
entry_new_code.grid(column=1, row=2)
label_add_new_value = tk.Label(main_frame, text="Value")
label_add_new_value.grid(column=2, row=2)
entry_new_value = tk.Entry(main_frame)
entry_new_value.grid(column=3, row=2)
button_add_new = tk.Button(main_frame, text="ADD", command=command_add_new, relief=tk.GROOVE)
button_add_new.grid(column=4, row=2)


if first_loop is True:
    update_snippets_menu()
    first_loop = False

root.mainloop()
