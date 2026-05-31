import csv
import datetime
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk
from tkcalendar import DateEntry


def read_csv_file(path: str | Path) -> list[dict]:
    """Read a Daylio CSV export and return its rows as a list of dicts.

    Args:
        path: Path to the Daylio CSV export file.

    Returns:
        A list of row dictionaries, one per CSV row.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a valid CSV.
    """
    with open(path, "r", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def write_csv_file(notes: list[dict], path: str | Path) -> None:
    """Write filtered notes to a pipe-delimited CSV file.

    Args:
        notes: List of dicts, each with ``date`` and ``note`` keys.
        path: Destination file path.
    """
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["date", "note"], delimiter="|")
        writer.writeheader()
        writer.writerows(notes)


def parse_date(row: dict) -> datetime.date:
    """Parse the ISO-format date from a Daylio CSV row.

    Args:
        row: A single row dict from :func:`read_csv_file`.

    Returns:
        A :class:`datetime.date` parsed from the ``full_date`` column.
    """
    return datetime.date.fromisoformat(row["full_date"])


def parse_note(row: dict) -> str:
    """Extract and clean the note text from a Daylio CSV row.

    Replaces Daylio's ``<br>`` HTML tags with real newlines and safely
    handles rows where the note column is absent or NaN.

    Args:
        row: A single row dict from :func:`read_csv_file`.

    Returns:
        The cleaned note string, or an empty string if no note is present.
    """
    raw = row.get("note")
    if not raw or raw != raw:  # Guards against None and float NaN (NaN != NaN)
        return ""
    return str(raw).replace("<br>", "\n")


def filter_notes(
    data: list[dict],
    start: datetime.date | None = None,
    end: datetime.date | None = None,
) -> list[dict]:
    """Filter Daylio rows to a date range and return cleaned date+note pairs.

    Args:
        data: Raw rows from :func:`read_csv_file`.
        start: Earliest date to include, inclusive. ``None`` means no lower
            bound.
        end: Latest date to include, inclusive. Defaults to today.

    Returns:
        A list of dicts, each with ``date`` (:class:`datetime.date`) and
        ``note`` (:class:`str`) keys, sorted descending by date.
    """
    if end is None:
        end = datetime.date.today()

    result = []
    for row in data:
        date = parse_date(row)
        after_start = start is None or date >= start
        before_end = date <= end
        if after_start and before_end:
            result.append({"date": date, "note": parse_note(row)})

    return result


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

_ONE_YEAR_AGO = datetime.date.today() - datetime.timedelta(days=365)


class App(ctk.CTk):
    """Main application window for Daylio CSV filtering."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Daylio Filter")
        self.geometry("480x360")
        self.resizable(False, False)

        self._build_ui()

    def _build_ui(self) -> None:
        """Construct and lay out all UI widgets."""
        # --- file selection ---
        ctk.CTkLabel(self, text="CSV File:").pack(pady=(20, 0))

        file_frame = ctk.CTkFrame(self, fg_color="transparent")
        file_frame.pack(fill="x", padx=20, pady=5)

        self._file_entry = ctk.CTkEntry(file_frame, placeholder_text="Select a Daylio export…")
        self._file_entry.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            file_frame, text="Browse", width=80, command=self._choose_input_file
        ).pack(side="right", padx=(8, 0))

        # --- date range ---
        date_frame = ctk.CTkFrame(self, fg_color="transparent")
        date_frame.pack(pady=15)

        ctk.CTkLabel(date_frame, text="Start Date:").grid(row=0, column=0, padx=10)
        ctk.CTkLabel(date_frame, text="End Date:").grid(row=0, column=1, padx=10)

        self._start_date = DateEntry(date_frame, date_pattern="yyyy-mm-dd")
        self._start_date.set_date(_ONE_YEAR_AGO)
        self._start_date.grid(row=1, column=0, padx=10)

        self._end_date = DateEntry(date_frame, date_pattern="yyyy-mm-dd")
        self._end_date.grid(row=1, column=1, padx=10)

        # --- process button ---
        ctk.CTkButton(self, text="Process", command=self._run_processing).pack(pady=5)

        # --- status ---
        self._status_label = ctk.CTkLabel(self, text="")
        self._status_label.pack(pady=10)

    def _choose_input_file(self) -> None:
        """Open a file dialog and populate the file entry with the chosen path."""
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            self._file_entry.delete(0, "end")
            self._file_entry.insert(0, path)

    def _run_processing(self) -> None:
        """Read, filter, and export the Daylio CSV based on current UI inputs."""
        input_path = self._file_entry.get().strip()
        if not input_path:
            self._set_status("Please select a CSV file.", error=True)
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="filtered_daylio.csv",
        )
        if not output_path:
            return

        try:
            start = self._start_date.get_date()
            end = self._end_date.get_date()

            if start > end:
                self._set_status("Start date must be before end date.", error=True)
                return

            data = read_csv_file(input_path)
            notes = filter_notes(data, start=start, end=end)
            write_csv_file(notes, output_path)

            self._set_status(f"Done ✅  —  {len(notes)} entries written.")

        except FileNotFoundError:
            self._set_status("Error: file not found.", error=True)
        except Exception as exc:
            self._set_status(f"Error: {exc}", error=True)

    def _set_status(self, message: str, *, error: bool = False) -> None:
        """Update the status label with a message.

        Args:
            message: Text to display.
            error: When ``True``, renders the text in red.
        """
        color = "#f87171" if error else "#86efac"
        self._status_label.configure(text=message, text_color=color)


if __name__ == "__main__":
    app = App()
    app.mainloop()
