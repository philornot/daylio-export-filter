import csv
import datetime


def read_csv_file(path):
    with open(path, 'r', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        return [row for row in csv_reader]


def write_csv_file(notes, path='filtered_daylio.csv'):
    with open(path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['date', 'note'],delimiter='|')
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
            notes.append({'date': date, 'note':f'{note}'})
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
