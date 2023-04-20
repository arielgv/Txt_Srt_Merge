import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Text, Scrollbar
import re

txt_filename = ""
srt_filename = ""

def parse_srt(srt_filename):
    with open(srt_filename, 'r') as file:
        content = file.read()
        pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n', re.DOTALL)
        matches = pattern.findall(content)
        srt_data = [{'index': int(m[0]), 'start': m[1], 'end': m[2], 'text': m[3]} for m in matches]
    return srt_data

def parse_txt(txt_filename):
    with open(txt_filename, 'r') as file:
        content = file.readlines()
        txt_data = []
        for line in content:
            if '=' in line and 's' in line:
                start_time = float(line.split('=')[1].split('s')[0].strip())
                speaker = line.split(' ')[-1].strip()
                txt_data.append({'start': start_time, 'speaker': speaker})
    return txt_data

def merge_srt_and_txt(srt_data, txt_data):
    merged_data = []
    txt_data_iter = iter(txt_data)

    for srt_item in srt_data:
        try:
            txt_item = next(txt_data_iter)
        except StopIteration:
            break

        speaker_label = txt_item['speaker'].replace('speaker_', '')

        merged_data.append({
            'index': srt_item['index'],
            'start': srt_item['start'],
            'end': srt_item['end'],
            'text': f'{speaker_label}: {srt_item["text"]}'
        })

    return merged_data

def merge_srt_and_txt_method_2(srt_data, txt_data, margin):
    merged_data = []
    margin = 2.6  # Margin of error in seconds
    last_speaker_label = None

    def srt_time_to_seconds(srt_time):
        hours, minutes, seconds = map(float, srt_time.replace(',', '.').split(':'))
        return hours * 3600 + minutes * 60 + seconds

    for srt_item in srt_data:
        srt_start_time = srt_time_to_seconds(srt_item['start'])
        speaker_label = None

        for txt_item in txt_data:
            if abs(srt_start_time - txt_item['start']) <= margin:
                speaker_label = txt_item['speaker'].replace('speaker_', '')
                last_speaker_label = speaker_label
                break

        # Si la línea de diálogo no tiene un speaker, usar el último speaker encontrado
        if not speaker_label and last_speaker_label:
            speaker_label = last_speaker_label

        # Agregar el speaker a la línea de diálogo si se encontró uno
        if speaker_label:
            merged_data.append({
                'index': srt_item['index'],
                'start': srt_item['start'],
                'end': srt_item['end'],
                'text': f'{speaker_label}: {srt_item["text"]}'
            })
        else:
            merged_data.append({
                'index': srt_item['index'],
                'start': srt_item['start'],
                'end': srt_item['end'],
                'text': srt_item['text']
            })

    return merged_data

def save_merged_srt(merged_data, output_filename):
    with open(output_filename, 'w') as file:
        for item in merged_data:
            file.write(f"{item['index']}\n")
            file.write(f"{item['start']} --> {item['end']}\n")
            file.write(f"{item['text']}\n\n")


def load_txt_file():
    global txt_filename
    txt_filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if txt_filename and srt_filename:
        merge_button.config(state=tk.NORMAL)
        preview_button.config(state=tk.NORMAL)
        files_loaded_label.config(text="TXT and SRT files loaded and ready")

def load_srt_file():
    global srt_filename
    srt_filename = filedialog.askopenfilename(filetypes=[("Subtitle files", "*.srt")])
    if txt_filename and srt_filename:
        merge_button.config(state=tk.NORMAL)
        preview_button.config(state=tk.NORMAL)
        files_loaded_label.config(text="TXT and SRT files loaded and ready")

def preview_merged_file():
    global srt_filename, txt_filename, margin_entry
    srt_data = parse_srt(srt_filename)
    txt_data = parse_txt(txt_filename)

    try:
        margin = float(margin_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number for the error margin")
        return
    
    merged_data = merge_srt_and_txt_method_2(srt_data, txt_data, margin)
    
    

    # Create the preview window
    preview_window = tk.Toplevel(app)
    preview_window.title("Merged SRT Preview")
    preview_window.geometry("600x400")

    # Create the Text widget and Scrollbar
    preview_text = Text(preview_window, wrap=tk.WORD)
    preview_scrollbar = Scrollbar(preview_window, command=preview_text.yview)
    preview_text.configure(yscrollcommand=preview_scrollbar.set)

    # Add the merged data to the Text widget
    for item in merged_data:
        preview_text.insert(tk.END, f"{item['index']}\n")
        preview_text.insert(tk.END, f"{item['start']} --> {item['end']}\n")
        preview_text.insert(tk.END, f"{item['text']}\n\n")

    # Place the Text widget and Scrollbar
    preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

def merge_files():
    global srt_filename, txt_filename, margin_entry
    srt_data = parse_srt(srt_filename)
    txt_data = parse_txt(txt_filename)

    try:
        margin = float(margin_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number for the error margin")
        return
    
    merged_data = merge_srt_and_txt_method_2(srt_data, txt_data, margin)
        
    output_filename = f"merged_{srt_filename.split('/')[-1]}"
    save_merged_srt(merged_data, output_filename)
    messagebox.showinfo("Done", "Merged SRT file has been created")

# Create the tkinter app
app = tk.Tk()
app.title("SRT Merger")
app.geometry("480x390")

# Create and place the widgets
error_margin_label = tk.Label(app, text="Error margin (sec):")
error_margin_label.pack(pady=10)
margin_entry = tk.Entry(app)
margin_entry.pack(pady=10)
margin_entry.insert(0, "2.5")  # Default value
load_txt_button = tk.Button(app, text="Load TXT file", command=load_txt_file)
load_txt_button.pack(pady=10)

load_srt_button = tk.Button(app, text="Load SRT file", command=load_srt_file)
load_srt_button.pack(pady=10)

files_loaded_label = tk.Label(app, text="")
files_loaded_label.pack(pady=10)

#method_var = tk.BooleanVar()
#method_var.set("Method 1")

#method_checkbox = tk.Checkbutton(app, text="Use Method 2: Time accuracy", variable=method_var, onvalue=True, offvalue=False)
#method_checkbox.pack(pady=10)

preview_button = tk.Button(app, text="Preview", state=tk.DISABLED, command=preview_merged_file)
preview_button.pack(pady=10)

merge_button = tk.Button(app, text="Merge", state=tk.DISABLED, command=merge_files)
merge_button.pack(pady=10)

error_margin_label = tk.Label(app, text="2.5 sec error margin")
error_margin_label.pack(pady=10)

# Add the following line to keep the window open
app.mainloop()
