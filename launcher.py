import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import sys
import os
import json
import threading

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
        """Extracts description based on the current language or fallback to string."""
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

        # Name row
        self._name_row = tk.Frame(self._inner, bg=CARD)
        self._name_row.pack(fill="x")
        tk.Label(self._name_row, text="⬡", fg=ACCENT2, bg=CARD, font=("Courier New", 13)).pack(side="left", padx=(0, 8))
        self._name_lbl = tk.Label(self._name_row, text=self.project["name"], fg=TEXT, bg=CARD, font=FONT_HEAD, anchor="w")
        self._name_lbl.pack(side="left", fill="x", expand=True)

        # Description (Localized)
        self._desc_lbl = tk.Label(self._inner, text=self._get_description(),
                                  fg=SUBTEXT, bg=CARD, font=FONT_SMALL,
                                  anchor="w", wraplength=500, justify="left")
        self._desc_lbl.pack(fill="x", pady=(3, 0))

        # Button + status row
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
            w.bind("<Enter>", self._on_enter); w.bind("<Leave>", self._on_leave)

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
        t = self.lang_fn(); col = self._STATE_COLORS.get(state, SUBTEXT); lbl = t.get(self._STATE_KEY.get(state, ""), "")
        self._status_dot.config(fg=col); self._status_lbl.config(fg=col, text=lbl)

    def refresh_lang(self):
        t = self.lang_fn()
        self._run_btn.config(text=t["run"])
        self._desc_lbl.config(text=self._get_description())
        self.set_status(self._state)

# ── Launcher window ───────────────────────────────────────────────────────────

class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self._lang = "en"
        self.projects = load_projects()
        self.cards = {}
        self.configure(bg=BG); self.geometry("720x650"); self.minsize(580, 440)
        self._build_ui(); self._refresh_list()

    def _t(self, key: str) -> str: return I18N[self._lang].get(key, key)
    def _lang_dict(self) -> dict: return I18N[self._lang]

    def _build_ui(self):
        hdr = tk.Frame(self, bg=PANEL, pady=16); hdr.pack(fill="x")
        self._title_lbl = tk.Label(hdr, text=self._t("title"), fg=ACCENT2, bg=PANEL, font=FONT_TITLE)
        self._title_lbl.pack(side="left", padx=22)

        lf = tk.Frame(hdr, bg=PANEL); lf.pack(side="right", padx=22)
        self._lang_btns = {}
        for code, label in [("en", "EN"), ("es", "ES"), ("pt", "PT")]:
            b = tk.Button(lf, text=label, font=FONT_LANG, width=4, relief="flat", cursor="hand2", pady=6, command=lambda c=code: self._switch_lang(c))
            b.pack(side="left", padx=3); self._lang_btns[code] = b
        self._style_lang_btns()

        self._hint_lbl = tk.Label(self, text=self._t("hint"), fg=WARN, bg=PANEL, font=FONT_SMALL, anchor="w", padx=16, pady=5)
        self._hint_lbl.pack(fill="x")

        sf = tk.Frame(self, bg=BG, pady=12, padx=20); sf.pack(fill="x")
        self._search_var = tk.StringVar(); self._search_var.trace_add("write", lambda *_: self._refresh_list())
        tk.Entry(sf, textvariable=self._search_var, bg=CARD, fg=TEXT, insertbackground=ACCENT2, relief="flat", font=FONT_BODY, highlightthickness=1, highlightcolor=ACCENT, highlightbackground=BORDER).pack(fill="x", expand=True, ipady=7)

        wrap = tk.Frame(self, bg=BG); wrap.pack(fill="both", expand=True, padx=20, pady=(0, 14))
        self._canvas = tk.Canvas(wrap, bg=BG, highlightthickness=0, bd=0)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self._canvas.yview); self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); self._canvas.pack(side="left", fill="both", expand=True)
        self._card_frame = tk.Frame(self._canvas, bg=BG)
        self._win_id = self._canvas.create_window((0, 0), window=self._card_frame, anchor="nw")
        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(self._win_id, width=e.width))
        self._card_frame.bind("<Configure>", lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._status_bar = tk.Label(self, text=self._t("ready"), fg=SUBTEXT, bg=PANEL, font=FONT_SMALL, anchor="w", padx=16, pady=6)
        self._status_bar.pack(fill="x", side="bottom"); self.title(self._t("title"))

    def _switch_lang(self, code: str):
        self._lang = code; self._style_lang_btns(); self._apply_lang()

    def _style_lang_btns(self):
        for code, btn in self._lang_btns.items():
            if code == self._lang: btn.config(bg=ACCENT, fg="white")
            else: btn.config(bg=CARD, fg=SUBTEXT)

    def _apply_lang(self):
        t = self._lang_dict()
        self.title(t["title"]); self._title_lbl.config(text=t["title"]); self._hint_lbl.config(text=t["hint"])
        self._status_bar.config(text=t["ready"])
        for card in self.cards.values(): card.refresh_lang()

    def _run_project(self, project: dict, card: "ProjectCard"):
        path = project["path"]
        if not os.path.exists(path):
            messagebox.showerror(self._t("not_found"), f"Path not found:\n{path}")
            return
        self._set_status(self._t("launching").format(project["name"])); card.set_status("running")

        def _worker():
            try:
                proc = subprocess.Popen([sys.executable, path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.path.dirname(path))
                self.after(0, lambda: self._set_status(self._t("launched").format(project["name"])))
                stdout, stderr = proc.communicate()
                status = "done" if proc.returncode == 0 else "error"
                msg = self._t("finished").format(project["name"]) if status == "done" else self._t("errored").format(project["name"])
                self.after(0, lambda: (card.set_status(status), self._set_status(msg)))
            except Exception as e:
                self.after(0, lambda: (card.set_status("error"), messagebox.showerror("Error", str(e))))
        threading.Thread(target=_worker, daemon=True).start()

    def _refresh_list(self):
        query = self._search_var.get().lower() if hasattr(self, "_search_var") else ""
        for w in self._card_frame.winfo_children(): w.destroy()
        self.cards.clear()

        visible = [p for p in self.projects if query in p["name"].lower() or query in p["path"].lower()]

        for proj in visible:
            card = ProjectCard(self._card_frame, proj, lang_fn=self._lang_dict, get_current_lang=lambda: self._lang, on_run=self._run_project)
            card.pack(fill="x", pady=(0, 10)); self.cards[proj["path"]] = card

    def _set_status(self, msg: str): self._status_bar.config(text=msg)

if __name__ == "__main__":
    app = Launcher()
    app.mainloop()