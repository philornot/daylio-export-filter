import csv
import datetime
from tkinter import filedialog

import customtkinter as ctk
from tkcalendar import DateEntry


def read_csv_file(path):
    with open(path, 'r', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        return [row for row in csv_reader]


def write_csv_file(notes, path='filtered_daylio.csv'):
    with open(path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['date', 'note'], delimiter='|')
        writer.writeheader()
        writer.writerows(notes)


def get_date(row_dict):
    day, month, year = row_dict['full_date'].split('-')
    return datetime.date(int(day), int(month), int(year))


def get_note(row_dict):
    note_key = 'note'
    return row_dict[note_key]


def format_note(note):
    return note.replace('<br>', '\n')


def filter_notes(data_list, start=False, end=None):
    if end is None:
        end = datetime.date.today()
    notes = []
    for row in data_list:
        date, note = get_date(row), get_note(row)
        if (not start and date <= end) or start <= date <= end:
            note = format_note(note)
            notes.append({'date': date, 'note': f'{note}'})
    return notes


def print_notes(notes):
    for note in notes:
        for date, text in note.items():
            print(f'==== {date} ====\n'
                  f'{text}\n\n')


FILE_PATH = 'daylio.csv'
OUTPUT_PATH = 'filtered.csv'
list_of_lines = read_csv_file(FILE_PATH)
start = datetime.date(2026, 1, 1)
notes = filter_notes(list_of_lines, start=start)
write_csv_file(notes, OUTPUT_PATH)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Daylio Filter")
        self.geometry("500x300")

        # --- file selection ---
        self.file_label = ctk.CTkLabel(self, text="CSV File:")
        self.file_label.pack(pady=(10, 0))

        self.file_entry = ctk.CTkEntry(self, width=400)
        self.file_entry.pack(pady=5)

        self.file_button = ctk.CTkButton(self, text="Choose File", command=self.choose_file)
        self.file_button.pack(pady=5)

        # --- dates ---
        self.start_label = ctk.CTkLabel(self, text="Start Date:")
        self.start_label.pack(pady=(10, 0))

        self.start_date = DateEntry(self, date_pattern='yyyy-mm-dd')
        self.start_date.pack(pady=5)

        self.end_label = ctk.CTkLabel(self, text="End Date:")
        self.end_label.pack(pady=(10, 0))

        self.end_date = DateEntry(self, date_pattern='yyyy-mm-dd')
        self.end_date.pack(pady=5)

        # --- button ---
        self.run_button = ctk.CTkButton(self, text="Process", command=self.run_processing)
        self.run_button.pack(pady=15)

        # --- status ---
        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.pack()

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, path)

    def run_processing(self):
        try:
            path = self.file_entry.get()

            start = self.start_date.get_date()
            end = self.end_date.get_date()

            data = read_csv_file(path)
            notes = filter_notes(data, start=start, end=end)
            write_csv_file(notes, OUTPUT_PATH)

            self.status_label.configure(text="Done")

        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()