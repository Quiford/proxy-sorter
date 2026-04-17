from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from proxysorter import convert_raw_lines, deduplicate_entries, read_non_empty_lines, save_proxies

DEFAULT_INPUT_FILE = "Fix.txt"
DEFAULT_OUTPUT_FILE = "proxy.txt"
TELEGRAM_HANDLE = "@Quiford"


def find_default_input() -> Path | None:
    for path in Path(".").rglob(DEFAULT_INPUT_FILE):
        return path
    return None


class ProxyFixerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Quiford Proxy Fixer")
        self.root.geometry("760x520")
        self.root.configure(bg="#0f172a")

        title = tk.Label(
            root,
            text="Quiford Proxy Fixer",
            font=("Segoe UI", 20, "bold"),
            bg="#0f172a",
            fg="#f8fafc",
        )
        title.pack(pady=(12, 2))

        subtitle = tk.Label(
            root,
            text="Convert host:port:user:password lines into scanner-ready format",
            font=("Segoe UI", 10),
            bg="#0f172a",
            fg="#94a3b8",
        )
        subtitle.pack(pady=(0, 8))

        self.log = tk.Text(
            root,
            width=94,
            height=22,
            bg="#111827",
            fg="#e5e7eb",
            insertbackground="#e5e7eb",
            relief="flat",
        )
        self.log.pack(padx=16, pady=8)

        controls = tk.Frame(root, bg="#0f172a")
        controls.pack(pady=8)

        tk.Button(
            controls,
            text="Scan for Fix.txt",
            width=18,
            command=self.scan_default_file,
            bg="#2563eb",
            fg="white",
            relief="flat",
        ).grid(row=0, column=0, padx=8)

        tk.Button(
            controls,
            text="Select File",
            width=18,
            command=self.select_file,
            bg="#16a34a",
            fg="white",
            relief="flat",
        ).grid(row=0, column=1, padx=8)

        tk.Button(
            controls,
            text="Clear Log",
            width=12,
            command=self.clear_log,
            bg="#334155",
            fg="white",
            relief="flat",
        ).grid(row=0, column=2, padx=8)

        self.footer = tk.Label(
            root,
            text=f"Contact Telegram: {TELEGRAM_HANDLE} for custom Python projects",
            font=("Segoe UI", 10, "bold"),
            bg="#0f172a",
            fg="#38bdf8",
        )
        self.footer.pack(pady=(6, 10))

    def write_log(self, message: str) -> None:
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)

    def clear_log(self) -> None:
        self.log.delete("1.0", tk.END)

    def process_file(self, source_path: Path) -> None:
        if not source_path.exists():
            messagebox.showerror("Error", f"File not found:\n{source_path}")
            return

        lines = read_non_empty_lines(source_path)
        converted, skipped = convert_raw_lines(lines, default_proxy_type="socks5")
        deduped = deduplicate_entries(converted)

        output_path = Path(DEFAULT_OUTPUT_FILE)
        save_proxies(output_path, deduped)

        self.write_log(f"[FILE] {source_path.resolve()}")
        self.write_log(f"[TOTAL] {len(lines)} lines read")
        self.write_log(f"[VALID] {len(converted)} converted")
        self.write_log(f"[UNIQUE] {len(deduped)} after dedupe")
        self.write_log(f"[SKIPPED] {len(skipped)} invalid lines")
        self.write_log(f"[SAVED] {output_path.resolve()}")

        if skipped:
            self.write_log("")
            self.write_log("[SKIPPED PREVIEW]")
            for line in skipped[:10]:
                self.write_log(f"- {line}")

        self.write_log("")
        self.write_log(f"Need help with Python projects? Telegram {TELEGRAM_HANDLE}")
        messagebox.showinfo(
            "Done",
            "Conversion completed.\n"
            f"Saved {len(deduped)} formatted proxies to {output_path.resolve()}",
        )

    def scan_default_file(self) -> None:
        discovered = find_default_input()
        if discovered is None:
            messagebox.showerror("Error", "Fix.txt not found in this project folder.")
            return
        self.process_file(discovered)

    def select_file(self) -> None:
        selected = filedialog.askopenfilename(
            title="Select raw proxy file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if selected:
            self.process_file(Path(selected))


if __name__ == "__main__":
    root = tk.Tk()
    app = ProxyFixerApp(root)
    root.mainloop()
