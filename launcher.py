import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import sys
import os
import json
import threading
import ast

# ── Config ───────────────────────────────────────────────────────────────────
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "launcher_projects.json")

# ── Palette ──────────────────────────────────────────────────────────────────
BG       = "#0d0d12"
PANEL    = "#16161f"
CARD     = "#1e1e2a"
CARD_HOV = "#272736"
ACCENT   = "#6d28d9"
ACCENT2  = "#a78bfa"
SUCCESS  = "#22c55e"
DANGER   = "#ef4444"
WARN     = "#f59e0b"
TEXT     = "#e2e8f0"
SUBTEXT  = "#94a3b8"
BORDER   = "#2a2a3c"

FONT_TITLE = ("Courier New", 20, "bold")
FONT_HEAD  = ("Courier New", 11, "bold")
FONT_BODY  = ("Courier New", 10)
FONT_SMALL = ("Courier New", 9)
FONT_BTN   = ("Courier New", 10, "bold")
FONT_LANG  = ("Courier New", 9,  "bold")

# ── Translations ─────────────────────────────────────────────────────────────
I18N = {
    "en": {
        "title":         "◈ EDUARDO's PYTHON PROJECTS",
        "run":           "▶  OPEN",
        "status_idle":   "idle",
        "status_run":    "running…",
        "status_done":   "finished",
        "status_err":    "error",
        "ready":         "Ready — select a project to launch it.",
        "launching":     "Launching: {}…",
        "launched":      "'{}' is now running independently.",
        "finished":      "'{}' has finished.",
        "errored":       "'{}' exited with an error.",
        "not_found":     "File not found",
        "not_found_msg": "Cannot find:\n{}",
        "err_title":     "Error",
        "no_projects":   "No projects configured.\nEdit launcher_projects.json to add entries.",
        "no_results":    "No results match your search.",
        "hint":          "Protected under Brazilian Law 9,610/98",
        "installing":    "Installing {}...",
        "install_success": "Module '{}' installed successfully. Re-running script...",
        "install_fail":   "Failed to install '{}'.\nError:\n{}",
    },
    "es": {
        "title":         "◈ PROYECTOS DE PYTHON DE EDUARDO",
        "run":           "▶  ABRIR",
        "status_idle":   "inactivo",
        "status_run":    "ejecutando…",
        "status_done":   "finalizado",
        "status_err":    "error",
        "ready":         "Listo — selecciona un proyecto para lanzarlo.",
        "launching":     "Lanzando: {}…",
        "launched":      "'{}' se está ejecutando de forma independiente.",
        "finished":      "'{}' ha finalizado.",
        "errored":       "'{}' salió con un error.",
        "not_found":     "Archivo no encontrado",
        "not_found_msg": "No se encuentra:\n{}",
        "err_title":     "Error",
        "no_projects":   "No hay proyectos configurados.\nEdita launcher_projects.json para agregar entradas.",
        "no_results":    "Ningún resultado coincide con tu búsqueda.",
        "hint":          "Protegido por la Ley Brasileña 9.610/98",
        "installing":    "Instalando {}...",
        "install_success": "Módulo '{}' instalado correctamente. Reejecutando script...",
        "install_fail":   "Error al instalar '{}'.\nError:\n{}",
    },
    "pt": {
        "title":         "◈ PROJETOS PYTHON DO EDUARDO",
        "run":           "▶  ABRIR",
        "status_idle":   "ocioso",
        "status_run":    "executando…",
        "status_done":   "finalizado",
        "status_err":    "erro",
        "ready":         "Pronto — selecione um projeto para lançá-lo.",
        "launching":     "Lançando: {}…",
        "launched":      "'{}' está sendo executado de forma independente.",
        "finished":      "'{}' finalizou.",
        "errored":       "'{}' saiu com um erro.",
        "not_found":     "Arquivo não encontrado",
        "not_found_msg": "Não é possível encontrar:\n{}",
        "err_title":     "Erro",
        "no_projects":   "Nenhum projeto configurado.\nEdite launcher_projects.json para adicionar entradas.",
        "no_results":    "Nenhum resultado corresponde à sua pesquisa.",
        "hint":          "Protegido pela Lei Brasileira nº 9.610/98",
        "installing":    "Instalando {}...",
        "install_success": "Módulo '{}' instalado com sucesso. Reexecutando script...",
        "install_fail":   "Falha ao instalar '{}'.\nErro:\n{}",
    },
}

def load_projects():
    base_dir = os.path.dirname(CONFIG_FILE)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                projects = json.load(f)
            for p in projects:
                if not os.path.isabs(p["path"]):
                    p["path"] = os.path.normpath(os.path.join(base_dir, p["path"]))
                if "args" not in p:
                    p["args"] = []
                elif isinstance(p["args"], str):
                    p["args"] = [p["args"]]
            return projects
        except Exception:
            pass
    return []

# ── Project Card ──────────────────────────────────────────────────────────────

class ProjectCard(tk.Frame):
    _STATE_COLORS = {"idle": "#94a3b8", "running": "#a78bfa", "done": "#22c55e", "error": "#ef4444"}
    _STATE_KEY = {"idle": "status_idle", "running": "status_run", "done": "status_done", "error": "status_err"}

    def __init__(self, parent, project, lang_fn, get_current_lang, on_run, **kwargs):
        super().__init__(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1, **kwargs)
        self.project = project
        self.lang_fn = lang_fn
        self.get_current_lang = get_current_lang
        self.on_run  = on_run
        self._state  = "idle"
        self._build()
        self._bind_hover(self._all_widgets())

    def _get_description(self):
        desc_data = self.project.get("description", "")
        curr_lang = self.get_current_lang()
        if isinstance(desc_data, dict):
            return desc_data.get(curr_lang, desc_data.get("en", "No description available."))
        return desc_data

    def _build(self):
        t = self.lang_fn()
        tk.Frame(self, bg=ACCENT, width=4).pack(side="left", fill="y")
        self._inner = tk.Frame(self, bg=CARD, padx=14, pady=12)
        self._inner.pack(side="left", fill="both", expand=True)

        self._name_row = tk.Frame(self._inner, bg=CARD)
        self._name_row.pack(fill="x")
        tk.Label(self._name_row, text="⬡", fg=ACCENT2, bg=CARD, font=("Courier New", 13)).pack(side="left", padx=(0, 8))
        self._name_lbl = tk.Label(self._name_row, text=self.project["name"], fg=TEXT, bg=CARD, font=FONT_HEAD, anchor="w")
        self._name_lbl.pack(side="left", fill="x", expand=True)

        self._desc_lbl = tk.Label(self._inner, text=self._get_description(),
                                  fg=SUBTEXT, bg=CARD, font=FONT_SMALL,
                                  anchor="w", wraplength=500, justify="left")
        self._desc_lbl.pack(fill="x", pady=(3, 0))

        self._btn_row = tk.Frame(self._inner, bg=CARD)
        self._btn_row.pack(fill="x", pady=(10, 0))
        self._run_btn = tk.Button(self._btn_row, text=t["run"], font=FONT_BTN, bg=ACCENT, fg="white", 
                                  relief="flat", padx=14, pady=5, cursor="hand2", command=lambda: self.on_run(self.project, self))
        self._run_btn.pack(side="left")

        self._status_dot = tk.Label(self._btn_row, text="●", fg=SUBTEXT, bg=CARD, font=("Courier New", 10))
        self._status_dot.pack(side="right", padx=(0, 2))
        self._status_lbl = tk.Label(self._btn_row, text=t["status_idle"], fg=SUBTEXT, bg=CARD, font=FONT_SMALL)
        self._status_lbl.pack(side="right")

    def _all_widgets(self):
        return [self, self._inner, self._name_row, self._name_lbl, self._desc_lbl, self._btn_row, self._status_dot, self._status_lbl]

    def _bind_hover(self, widgets):
        for w in widgets:
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)

    def _on_enter(self, _):
        for w in self._all_widgets(): 
            try: w.config(bg=CARD_HOV)
            except: pass

    def _on_leave(self, _):
        for w in self._all_widgets():
            try: w.config(bg=CARD)
            except: pass

    def set_status(self, state: str):
        self._state = state
        t = self.lang_fn()
        col = self._STATE_COLORS.get(state, SUBTEXT)
        lbl = t.get(self._STATE_KEY.get(state, ""), "")
        self._status_dot.config(fg=col)
        self._status_lbl.config(fg=col, text=lbl)

    def refresh_lang(self):
        t = self.lang_fn()
        self._run_btn.config(text=t["run"])
        self._desc_lbl.config(text=self._get_description())
        self.set_status(self._state)

# ── Embedded Terminal Window ──────────────────────────────────────────────────

class TerminalWindow(tk.Toplevel):
    """
    Embedded Tkinter terminal: runs a subprocess, streams its stdout/stderr
    into a Text widget in real-time (character-by-character, binary reads so
    prompts without newlines appear immediately), and sends user input to stdin.
    Works on all platforms — no external terminal required.
    """

    _POLL_MS = 30   # how often (ms) to drain the output queue into the widget

    def __init__(self, parent, project_name: str, cmd: list, cwd: str, on_done_cb=None):
        super().__init__(parent)
        self.title(f"◈ {project_name}")
        self.geometry("700x480")
        self.minsize(500, 340)
        self.configure(bg=BG)
        self._on_done_cb = on_done_cb
        self._proc       = None
        self._closed     = False
        # Thread-safe queue: items are (text, tag) tuples
        import queue
        self._queue = queue.Queue()

        self._build_ui(project_name)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._start_process(cmd, cwd)
        self._poll_queue()   # start the Tkinter-side drain loop

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self, project_name: str):
        # ── header ──
        hdr = tk.Frame(self, bg=PANEL, pady=8, padx=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"⬡ {project_name}", fg=ACCENT2, bg=PANEL,
                 font=FONT_HEAD).pack(side="left")
        self._status_lbl = tk.Label(hdr, text="● running", fg=ACCENT2,
                                    bg=PANEL, font=FONT_SMALL)
        self._status_lbl.pack(side="right")

        # ── input bar (packed before output so it's always at the bottom) ──
        inp_frame = tk.Frame(self, bg=PANEL, pady=8, padx=10)
        inp_frame.pack(fill="x", side="bottom")

        tk.Label(inp_frame, text="›", fg=ACCENT2, bg=PANEL,
                 font=("Courier New", 14, "bold")).pack(side="left", padx=(0, 6))

        self._input_var = tk.StringVar()
        self._entry = tk.Entry(
            inp_frame, textvariable=self._input_var,
            bg=CARD, fg=TEXT, insertbackground=ACCENT2,
            relief="flat", font=FONT_BODY,
            highlightthickness=1, highlightcolor=ACCENT, highlightbackground=BORDER,
        )
        self._entry.pack(side="left", fill="x", expand=True, ipady=6)
        self._entry.bind("<Return>", self._on_submit)
        self._entry.focus_set()

        tk.Button(
            inp_frame, text="Send", font=FONT_BTN, bg=ACCENT, fg="white",
            relief="flat", padx=12, pady=4, cursor="hand2",
            command=self._on_submit,
        ).pack(side="left", padx=(8, 0))

        # ── output area ──
        out_frame = tk.Frame(self, bg=BG)
        out_frame.pack(fill="both", expand=True, padx=10, pady=(8, 4))

        self._output = tk.Text(
            out_frame, bg="#0a0a10", fg=TEXT, font=FONT_BODY,
            wrap="word", relief="flat", borderwidth=0,
            state="disabled", cursor="arrow",
        )
        sb = ttk.Scrollbar(out_frame, orient="vertical", command=self._output.yview)
        self._output.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._output.pack(side="left", fill="both", expand=True)

        # colour tags
        self._output.tag_configure("echo",   foreground=ACCENT2)   # user's typed input
        self._output.tag_configure("stderr", foreground=DANGER)
        self._output.tag_configure("info",   foreground=WARN)

    # ── Process management ────────────────────────────────────────────────────

    def _start_process(self, cmd: list, cwd: str):
        try:
            self._proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                # binary mode + no buffering = prompts appear the instant they're written
                bufsize=0,
            )
        except Exception as e:
            self._queue.put((f"[ERROR] Could not start process:\n{e}\n", "stderr"))
            self._queue.put(("__EXIT__", 1))
            return

        threading.Thread(target=self._reader, args=(self._proc.stdout, ""),
                         daemon=True).start()
        threading.Thread(target=self._reader, args=(self._proc.stderr, "stderr"),
                         daemon=True).start()
        threading.Thread(target=self._monitor, daemon=True).start()

    def _reader(self, stream, tag: str):
        """
        Read raw bytes one-by-one from the stream.
        Accumulate into a buffer; flush to the queue either on newline
        OR after a short idle gap (so prompts without \\n show up immediately).
        """
        import time
        buf = b""
        while True:
            try:
                ch = stream.read(1)
            except Exception:
                break
            if not ch:
                break
            buf += ch
            # Flush on newline so normal output lines appear atomically,
            # but also flush on any non-newline character when the buffer
            # already has content — this makes prompts like "Change: " visible
            # without waiting for a newline that never comes.
            if ch == b"\n" or (buf and ch != b"\n"):
                text = buf.decode("utf-8", errors="replace")
                self._queue.put((text, tag))
                buf = b""
        if buf:
            self._queue.put((buf.decode("utf-8", errors="replace"), tag))

    def _monitor(self):
        if self._proc:
            self._proc.wait()
            self._queue.put(("__EXIT__", self._proc.returncode))

    # ── Queue → UI drain loop (runs on the main thread via after()) ───────────

    def _poll_queue(self):
        if self._closed:
            return
        # Drain everything currently in the queue in one Tkinter call burst
        try:
            while True:
                item = self._queue.get_nowait()
                text, tag = item
                if text == "__EXIT__":
                    self._mark_finished(tag)   # tag holds the returncode here
                    return                     # stop polling
                self._append(text, tag)
        except Exception:
            pass
        self.after(self._POLL_MS, self._poll_queue)

    def _append(self, text: str, tag: str = ""):
        self._output.config(state="normal")
        if tag:
            self._output.insert("end", text, tag)
        else:
            self._output.insert("end", text)
        self._output.config(state="disabled")
        self._output.see("end")

    def _mark_finished(self, returncode: int):
        if self._closed:
            return
        ok = returncode == 0
        self._status_lbl.config(
            text="● finished" if ok else f"● exited ({returncode})",
            fg=SUCCESS if ok else DANGER,
        )
        self._entry.config(state="disabled")
        self._append(f"\n[Process exited with code {returncode}]\n", "info")
        if self._on_done_cb:
            self._on_done_cb(returncode)

    # ── User input ────────────────────────────────────────────────────────────

    def _on_submit(self, _event=None):
        text = self._input_var.get()
        self._input_var.set("")
        if not text and self._proc and self._proc.poll() is not None:
            return
        if self._proc and self._proc.stdin and not self._proc.stdin.closed:
            try:
                # Echo what the user typed so the terminal looks natural
                self._append(text + "\n", "echo")
                self._proc.stdin.write((text + "\n").encode())
                self._proc.stdin.flush()
            except Exception:
                pass

    # ── Close ─────────────────────────────────────────────────────────────────

    def _on_close(self):
        self._closed = True
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
            except Exception:
                pass
        self.destroy()


# ── Launcher window ───────────────────────────────────────────────────────────

class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self._lang = "en"
        self.projects = load_projects()
        self.cards = {}
        self.configure(bg=BG)
        self.geometry("720x650")
        self.minsize(580, 440)
        self._build_ui()
        self._refresh_list()

    def _t(self, key: str) -> str:
        return I18N[self._lang].get(key, key)

    def _lang_dict(self) -> dict:
        return I18N[self._lang]

    def _build_ui(self):
        hdr = tk.Frame(self, bg=PANEL, pady=16)
        hdr.pack(fill="x")
        self._title_lbl = tk.Label(hdr, text=self._t("title"), fg=ACCENT2, bg=PANEL, font=FONT_TITLE)
        self._title_lbl.pack(side="left", padx=22)

        lf = tk.Frame(hdr, bg=PANEL)
        lf.pack(side="right", padx=22)
        self._lang_btns = {}
        for code, label in [("en", "EN"), ("es", "ES"), ("pt", "PT")]:
            b = tk.Button(lf, text=label, font=FONT_LANG, width=4, relief="flat", cursor="hand2", pady=6, command=lambda c=code: self._switch_lang(c))
            b.pack(side="left", padx=3)
            self._lang_btns[code] = b
        self._style_lang_btns()

        self._hint_lbl = tk.Label(self, text=self._t("hint"), fg=WARN, bg=PANEL, font=FONT_SMALL, anchor="w", padx=16, pady=5)
        self._hint_lbl.pack(fill="x")

        sf = tk.Frame(self, bg=BG, pady=12, padx=20)
        sf.pack(fill="x")
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh_list())
        tk.Entry(sf, textvariable=self._search_var, bg=CARD, fg=TEXT, insertbackground=ACCENT2, relief="flat", font=FONT_BODY, highlightthickness=1, highlightcolor=ACCENT, highlightbackground=BORDER).pack(fill="x", expand=True, ipady=7)

        wrap = tk.Frame(self, bg=BG)
        wrap.pack(fill="both", expand=True, padx=20, pady=(0, 14))
        self._canvas = tk.Canvas(wrap, bg=BG, highlightthickness=0, bd=0)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)
        self._card_frame = tk.Frame(self._canvas, bg=BG)
        self._win_id = self._canvas.create_window((0, 0), window=self._card_frame, anchor="nw")
        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(self._win_id, width=e.width))
        self._card_frame.bind("<Configure>", lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._status_bar = tk.Label(self, text=self._t("ready"), fg=SUBTEXT, bg=PANEL, font=FONT_SMALL, anchor="w", padx=16, pady=6)
        self._status_bar.pack(fill="x", side="bottom")
        self.title(self._t("title"))

    def _switch_lang(self, code: str):
        self._lang = code
        self._style_lang_btns()
        self._apply_lang()

    def _style_lang_btns(self):
        for code, btn in self._lang_btns.items():
            if code == self._lang:
                btn.config(bg=ACCENT, fg="white")
            else:
                btn.config(bg=CARD, fg=SUBTEXT)

    def _apply_lang(self):
        t = self._lang_dict()
        self.title(t["title"])
        self._title_lbl.config(text=t["title"])
        self._hint_lbl.config(text=t["hint"])
        self._status_bar.config(text=t["ready"])
        for card in self.cards.values():
            card.refresh_lang()

    def _get_imported_modules(self, script_path: str) -> set:
        """Extract top-level module names from import statements, via the AST
        (handles `import x as y`, `import a, b`, relative imports, etc.
        correctly — a hand-rolled string parser gets these wrong)."""
        modules = set()
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=script_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        modules.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.level == 0:  # skip relative imports
                        modules.add(node.module.split(".")[0])
        except Exception:
            pass
        return modules

    # Import name -> PyPI package name, for the handful of common cases
    # where they differ. Keep this short; it's a fallback, not a registry.
    _PIP_NAME_OVERRIDES = {
        "PIL": "Pillow",
        "cv2": "opencv-python",
        "yaml": "PyYAML",
        "bs4": "beautifulsoup4",
        "sklearn": "scikit-learn",
        "dotenv": "python-dotenv",
    }

    def _ensure_modules_installed(self, project: dict, card: "ProjectCard") -> bool:
        """Check if all imported modules are installed; if not, ask to install."""
        path = project["path"]
        modules = self._get_imported_modules(path)
        stdlib = getattr(sys, "stdlib_module_names", set())
        missing = []
        for mod in modules:
            if mod in stdlib:
                continue
            try:
                subprocess.run([sys.executable, "-c", f"import {mod}"], capture_output=True, check=True, timeout=5)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                missing.append(mod)
        if not missing:
            return True

        pip_names = [self._PIP_NAME_OVERRIDES.get(mod, mod) for mod in missing]
        if len(missing) == 1:
            msg = f"Module '{missing[0]}' is required but not installed.\nInstall it now using pip?"
        else:
            msg = f"Modules: {', '.join(missing)} are required but not installed.\nInstall them now using pip?"
        if not messagebox.askyesno(self._t("err_title"), msg):
            card.set_status("error")
            self._set_status(self._t("errored").format(project["name"]))
            return False

        for mod in pip_names:
            self._set_status(self._t("installing").format(mod))
            try:
                proc = subprocess.run([sys.executable, "-m", "pip", "install", mod],
                                      capture_output=True, text=True, timeout=60)
                if proc.returncode != 0:
                    error_msg = proc.stderr or proc.stdout or "Unknown error"
                    self.after(0, lambda m=mod, e=error_msg: messagebox.showerror(
                        self._t("err_title"),
                        self._t("install_fail").format(m, e)
                    ))
                    card.set_status("error")
                    self._set_status(self._t("errored").format(project["name"]))
                    return False
            except Exception as e:
                self.after(0, lambda m=mod, e=str(e): messagebox.showerror(
                    self._t("err_title"),
                    self._t("install_fail").format(m, e)
                ))
                card.set_status("error")
                self._set_status(self._t("errored").format(project["name"]))
                return False
        self._set_status(self._t("install_success").format(", ".join(pip_names)))
        return True

    def _open_terminal_window(self, project: dict, card: "ProjectCard"):
        """Open the embedded Tkinter terminal window for the project."""
        if not self._ensure_modules_installed(project, card):
            return
        path = project["path"]
        cwd = os.path.dirname(path)
        cmd = [sys.executable, "-u", path] + project.get("args", [])
        self._set_status(self._t("launching").format(project["name"]))
        card.set_status("running")
        def on_done(returncode):
            status = "done" if returncode == 0 else "error"
            msg = (self._t("finished").format(project["name"]) if status == "done"
                   else self._t("errored").format(project["name"]))
            self.after(0, lambda: (card.set_status(status), self._set_status(msg)))
        TerminalWindow(self, project["name"], cmd, cwd, on_done)

    def _run_project(self, project: dict, card: "ProjectCard", retry=False):
        path = project["path"]
        if not os.path.exists(path):
            messagebox.showerror(self._t("not_found"), f"Path not found:\n{path}")
            return
        # Always use the embedded terminal window
        self._open_terminal_window(project, card)

    def _refresh_list(self):
        query = self._search_var.get().lower() if hasattr(self, "_search_var") else ""
        for w in self._card_frame.winfo_children():
            w.destroy()
        self.cards.clear()

        visible = [p for p in self.projects if query in p["name"].lower() or query in p["path"].lower()]

        for proj in visible:
            card = ProjectCard(self._card_frame, proj, lang_fn=self._lang_dict, get_current_lang=lambda: self._lang, on_run=self._run_project)
            card.pack(fill="x", pady=(0, 10))
            self.cards[proj["path"]] = card

    def _set_status(self, msg: str):
        self._status_bar.config(text=msg)

if __name__ == "__main__":
    app = Launcher()
    app.mainloop()
