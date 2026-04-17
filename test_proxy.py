from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from proxysorter import (
    ProxyCheckResult,
    ProxyStatus,
    check_proxies,
    load_proxies,
    save_proxies,
    summarize_results,
    working_proxies,
)

DEFAULT_PROXY_FILE = "proxy.txt"
DEFAULT_OUTPUT_FILE = "working_proxy.txt"
TELEGRAM_HANDLE = "@Quiford"

THEME = {
    "bg": "#0b1020",
    "panel": "#111827",
    "text": "#e5e7eb",
    "muted": "#94a3b8",
    "green": "#22c55e",
    "red": "#ef4444",
    "yellow": "#f59e0b",
    "blue": "#38bdf8",
}


class QuifordProxyChecker:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Quiford Proxy Checker")
        self.root.geometry("1220x760")
        self.root.configure(bg=THEME["bg"])

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "Treeview",
            background=THEME["panel"],
            fieldbackground=THEME["panel"],
            foreground=THEME["text"],
            rowheight=28,
        )
        self.style.configure("Treeview.Heading", background="#0f172a", foreground="white")
        self.style.configure(
            "green.Horizontal.TProgressbar",
            troughcolor=THEME["panel"],
            background=THEME["green"],
            thickness=18,
        )

        self.proxies = []
        self.results: list[ProxyCheckResult | None] = []
        self.items_by_index: dict[int, str] = {}
        self.current_file = Path(DEFAULT_PROXY_FILE)

        self.running = False
        self.scan_thread: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.done_count = 0

        self.build_ui()

    def build_ui(self) -> None:
        tk.Label(
            self.root,
            text="QUIFORD PROXY CHECKER",
            bg=THEME["bg"],
            fg="white",
            font=("Segoe UI", 20, "bold"),
        ).pack(pady=(12, 4))

        tk.Label(
            self.root,
            text="Load formatted proxies, scan them fast, and export only working entries",
            bg=THEME["bg"],
            fg=THEME["muted"],
            font=("Segoe UI", 10),
        ).pack()

        button_bar = tk.Frame(self.root, bg=THEME["bg"])
        button_bar.pack(pady=10)

        tk.Button(
            button_bar,
            text="Load File",
            command=self.load_file_dialog,
            bg="#2563eb",
            fg="white",
            width=14,
            relief="flat",
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            button_bar,
            text="Start Scan",
            command=self.start_scan,
            bg=THEME["green"],
            fg="black",
            width=14,
            relief="flat",
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            button_bar,
            text="Stop",
            command=self.stop_scan,
            bg=THEME["red"],
            fg="white",
            width=14,
            relief="flat",
        ).grid(row=0, column=2, padx=5)

        tk.Button(
            button_bar,
            text="Export Working",
            command=self.export_working,
            bg="#0ea5e9",
            fg="white",
            width=14,
            relief="flat",
        ).grid(row=0, column=3, padx=5)

        self.progress = ttk.Progressbar(
            self.root,
            length=1120,
            mode="determinate",
            style="green.Horizontal.TProgressbar",
        )
        self.progress.pack(pady=10)

        table_frame = tk.Frame(self.root, bg=THEME["bg"])
        table_frame.pack(fill="both", expand=True, padx=15)

        columns = ("type", "host", "port", "user", "status", "latency", "error")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.pack(fill="both", expand=True)

        widths = {
            "type": 110,
            "host": 210,
            "port": 80,
            "user": 170,
            "status": 110,
            "latency": 100,
            "error": 420,
        }
        for column in columns:
            self.tree.heading(column, text=column.upper())
            self.tree.column(column, anchor="center", width=widths[column], stretch=True)

        self.tree.tag_configure("WORKING", foreground=THEME["green"])
        self.tree.tag_configure("FAILED", foreground=THEME["red"])
        self.tree.tag_configure("INVALID", foreground=THEME["yellow"])
        self.tree.tag_configure("PENDING", foreground=THEME["muted"])
        self.tree.tag_configure("SKIPPED", foreground=THEME["blue"])

        self.stats_label = tk.Label(
            self.root,
            text="Load a formatted proxy file to begin.",
            bg=THEME["bg"],
            fg=THEME["muted"],
            font=("Segoe UI", 11, "bold"),
        )
        self.stats_label.pack(fill="x", padx=12, pady=(8, 4))

        self.file_label = tk.Label(
            self.root,
            text=f"Current file: {self.current_file.resolve()}",
            bg=THEME["bg"],
            fg=THEME["muted"],
            font=("Segoe UI", 9),
        )
        self.file_label.pack(fill="x", padx=12)

        self.footer = tk.Label(
            self.root,
            text=f"Contact Telegram: {TELEGRAM_HANDLE} for custom Python projects",
            bg=THEME["bg"],
            fg=THEME["blue"],
            font=("Segoe UI", 10, "bold"),
        )
        self.footer.pack(pady=(6, 10))

    def set_stats(self) -> None:
        summary = summarize_results([r for r in self.results if r is not None])
        total = len(self.proxies)
        message = (
            f"TOTAL: {total} | "
            f"WORKING: {summary.get('WORKING', 0)} | "
            f"FAILED: {summary.get('FAILED', 0)} | "
            f"INVALID: {summary.get('INVALID', 0)} | "
            f"SKIPPED: {summary.get('SKIPPED', 0)}"
        )
        self.stats_label.config(text=message)

    def load_file_dialog(self) -> None:
        chosen = filedialog.askopenfilename(
            title="Select formatted proxy file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if chosen:
            self.load_proxies(Path(chosen))

    def load_proxies(self, path: Path | None = None) -> None:
        if path is not None:
            self.current_file = path
        if not self.current_file.exists():
            messagebox.showerror("Error", f"File not found:\n{self.current_file.resolve()}")
            return

        proxies, invalid = load_proxies(self.current_file)
        if not proxies:
            messagebox.showerror("Error", "No valid proxy lines found in selected file.")
            return

        self.proxies = proxies
        self.results = [None] * len(self.proxies)
        self.items_by_index.clear()
        self.done_count = 0
        self.running = False

        self.progress["maximum"] = len(self.proxies)
        self.progress["value"] = 0
        self.tree.delete(*self.tree.get_children())

        for index, proxy in enumerate(self.proxies):
            item = self.tree.insert(
                "",
                "end",
                values=(
                    proxy.proxy_type,
                    proxy.host,
                    proxy.port,
                    proxy.username,
                    ProxyStatus.PENDING.value,
                    "-",
                    "",
                ),
                tags=(ProxyStatus.PENDING.value,),
            )
            self.items_by_index[index] = item

        self.file_label.config(text=f"Current file: {self.current_file.resolve()}")
        self.set_stats()

        if invalid:
            messagebox.showwarning(
                "Warning",
                f"Loaded {len(proxies)} proxies. Ignored {len(invalid)} invalid lines.",
            )

    def start_scan(self) -> None:
        if self.running:
            return

        if not self.proxies:
            default_path = Path(DEFAULT_PROXY_FILE)
            if default_path.exists():
                self.load_proxies(default_path)
            else:
                messagebox.showinfo("Info", "Load a proxy file first.")
                return

        self.running = True
        self.stop_event.clear()
        self.done_count = 0
        self.progress["value"] = 0
        self.results = [None] * len(self.proxies)

        self.scan_thread = threading.Thread(target=self._run_scan, daemon=True)
        self.scan_thread.start()

    def stop_scan(self) -> None:
        if self.running:
            self.stop_event.set()
            self.stats_label.config(text="Stopping scan...")

    def _run_scan(self) -> None:
        def on_result(index: int, result: ProxyCheckResult) -> None:
            if not self.running:
                return
            self.root.after(0, self._apply_result, index, result)

        results = check_proxies(
            self.proxies,
            max_workers=80,
            target_host="1.1.1.1",
            target_port=443,
            tcp_timeout=4.0,
            proxy_timeout=8.0,
            callback=on_result,
            stop_event=self.stop_event,
        )

        self.root.after(0, self._finish_scan, results)

    def _apply_result(self, index: int, result: ProxyCheckResult) -> None:
        if index >= len(self.results):
            return
        self.results[index] = result
        self.done_count += 1
        self.progress["value"] = self.done_count

        item = self.items_by_index.get(index)
        if item:
            latency = "-" if result.latency_ms is None else f"{result.latency_ms} ms"
            self.tree.item(
                item,
                values=(
                    result.proxy.proxy_type,
                    result.proxy.host,
                    result.proxy.port,
                    result.proxy.username,
                    result.status.value,
                    latency,
                    result.error,
                ),
                tags=(result.status.value,),
            )

        self.set_stats()

    def _finish_scan(self, results: list[ProxyCheckResult]) -> None:
        self.running = False
        self.results = results
        self.set_stats()
        working_count = len(working_proxies(results))
        if self.stop_event.is_set():
            messagebox.showinfo(
                "Scan Stopped",
                f"Scan was stopped.\n"
                f"Working proxies found so far: {working_count}\n"
                f"Use 'Export Working' to save them to {DEFAULT_OUTPUT_FILE}.",
            )
            return
        messagebox.showinfo(
            "Scan Finished",
            f"Completed scan.\nWorking proxies: {working_count}\n"
            f"Use 'Export Working' to save them to {DEFAULT_OUTPUT_FILE}.",
        )

    def export_working(self) -> None:
        if not self.results:
            messagebox.showinfo("Info", "No scan results to export.")
            return

        working = working_proxies([r for r in self.results if r is not None])
        if not working:
            messagebox.showwarning("Export", "No working proxies found.")
            return

        suggested = self.current_file.parent / DEFAULT_OUTPUT_FILE
        selected = filedialog.asksaveasfilename(
            title="Save working proxies",
            defaultextension=".txt",
            initialfile=suggested.name,
            initialdir=str(suggested.parent),
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not selected:
            return

        save_proxies(selected, working)
        messagebox.showinfo("Exported", f"Saved {len(working)} working proxies to:\n{selected}")


if __name__ == "__main__":
    root = tk.Tk()
    app = QuifordProxyChecker(root)
    app.load_proxies(Path(DEFAULT_PROXY_FILE))
    root.mainloop()
