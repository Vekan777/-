#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Offline graphical front-end for AI Rescue Factory V7 on Windows.
Uses Tkinter (normally shipped with Windows CPython) and safe argv subprocess.
"""
from __future__ import annotations
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

BASE = Path(__file__).resolve().parent
V7 = BASE / "rescue-engine" / "unified_v7.py"
V19 = BASE / "anime-factory" / "v19" / "AI_Anime_Factory_V19.html"
V20 = BASE / "anime-factory" / "v20" / "AI_Anime_Factory_V20_3_PRESERVATION.html"
V20_STORY = BASE / "anime-factory" / "v20" / "AI_Anime_Factory_V20_STORY_COMBAT.html"
V21_VISUAL = BASE / "anime-factory" / "v21" / "AI_Anime_Factory_V21_VISUAL_QUALITY.html"
V22_ACTING = BASE / "anime-factory" / "v22" / "AI_Anime_Factory_V22_ACTING_COMBAT.html"
V23_CHARACTER = BASE / "anime-factory" / "v23" / "AI_Anime_Factory_V23_CHARACTER_QUALITY.html"
V24_ANIMATION = BASE / "anime-factory" / "v24" / "AI_Anime_Factory_V24_CHARACTER_ANIMATION.html"
V25_COMBAT = BASE / "anime-factory" / "v25" / "AI_Anime_Factory_V25_COMBAT_CHOREOGRAPHY.html"
V26_CINEMA = BASE / "anime-factory" / "v26" / "AI_Anime_Factory_V26_CINEMATIC_COMBAT.html"
V27_WORLD = BASE / "anime-factory" / "v27" / "AI_Anime_Factory_V27_WORLD_QUALITY.html"
V28_INTERACTION = BASE / "anime-factory" / "v28" / "AI_Anime_Factory_V28_CHARACTER_WORLD_INTERACTION.html"
V29_POLISH = BASE / "anime-factory" / "v29" / "AI_Anime_Factory_V29_ANIMATION_COMBAT_POLISH.html"
V30_REVIEW = BASE / "anime-factory" / "v30" / "AI_Anime_Factory_V30_UNIFIED_QUALITY_REVIEW.html"
V31_VISUAL = BASE / "anime-factory" / "v31" / "AI_Anime_Factory_V31_VISUAL_PRODUCTION_REVIEW.html"
V32_KEYFRAMES = BASE / "anime-factory" / "v32" / "AI_Anime_Factory_V32_KEYFRAME_READABILITY.html"
V33_ACTING = BASE / "anime-factory" / "v33" / "AI_Anime_Factory_V33_ACTING_EXPRESSION.html"
V34_STORYBOARD = BASE / "anime-factory" / "v34" / "AI_Anime_Factory_V34_STORYBOARD_CONTINUITY.html"
V35_ASSEMBLY = BASE / "anime-factory" / "v35" / "AI_Anime_Factory_V35_SCENE_ASSEMBLY.html"
V36_AUDIO = BASE / "anime-factory" / "v36" / "AI_Anime_Factory_V36_AUDIO_EPISODE_EXPORT.html"
V37_SUBTITLES = BASE / "anime-factory" / "v37" / "AI_Anime_Factory_V37_SUBTITLES_DELIVERY.html"
V38_CINEMA = BASE / "anime-factory" / "v38" / "AI_Anime_Factory_V38_CINEMATIC_FINISHING.html"
V39_ACTION = BASE / "anime-factory" / "v39" / "AI_Anime_Factory_V39_CHARACTER_ACTION.html"
V40_ART = BASE / "anime-factory" / "v40" / "AI_Anime_Factory_V40_CHARACTER_ART.html"
V41_SILHOUETTES = BASE / "anime-factory" / "v41" / "AI_Anime_Factory_V41_SILHOUETTE_STUDIO.html"
V42_STAGE = BASE / "anime-factory" / "v42" / "AI_Anime_Factory_V42_STAGE_DEPTH.html"
V43_DIRECTOR = BASE / "anime-factory" / "v43" / "AI_Anime_Factory_V43_ACTION_DIRECTOR.html"
V44_KEYPOSES = BASE / "anime-factory" / "v44" / "AI_Anime_Factory_V44_TRUE_KEYPOSES.html"
V45_ART_ENGINE = BASE / "anime-factory" / "v45" / "AI_Anime_Factory_V45_ART_ENGINE.html"
V46_ANIMATION = BASE / "anime-factory" / "v46" / "AI_Anime_Factory_V46_ANIMATION_ENGINE.html"
V47_VOICE = BASE / "anime-factory" / "v47" / "AI_Anime_Factory_V47_PORTABLE_VOICE.html"
V48_EPISODE = BASE / "anime-factory" / "v48" / "AI_Anime_Factory_V48_EPISODE_ENGINE.html"


class Studio:
    def __init__(self, win):
        self.win = win
        win.title("AI Rescue Factory V7 — Unified Studio")
        win.geometry("860x650")
        win.minsize(660, 480)
        self.project = tk.StringVar(value="default")
        self.busy = False

        header = ttk.Frame(win, padding=12)
        header.pack(fill="x")
        ttk.Label(header, text="AI RESCUE FACTORY V7", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(header, text="Автономная сборка ZIP • Резервные копии • Восстановление • V19–V48",
                  font=("Segoe UI", 10)).pack(anchor="w")
        controls = ttk.Frame(win, padding=(12, 4))
        controls.pack(fill="x")
        ttk.Label(controls, text="Проект:").pack(side="left")
        ttk.Entry(controls, textvariable=self.project, width=28).pack(side="left", padx=(9, 12))
        ttk.Button(controls, text="Состояние", command=lambda: self.command("status")).pack(side="left")
        ttk.Button(controls, text="Диагностика", command=lambda: self.command("doctor")).pack(side="left", padx=6)

        buttons = ttk.Frame(win, padding=12)
        buttons.pack(fill="x")
        entries = [
            ("Самопроверка V7", lambda: self.command("selftest")),
            ("Резервный ZIP", lambda: self.command("backup")),
            ("Выпустить ZIP", lambda: self.command("release")),
            ("Проверить проект", lambda: self.command("audit")),
            ("Проверить ZIP V7", self.verify_bundle),
            ("Проверить ZIP проекта", self.verify_project),
            ("Импорт старого ZIP", self.import_zip),
            ("Перенос проекта V1–V6", self.migrate),
            ("Добавить задание в очередь", self.enqueue),
            ("Выполнить 1 задание", lambda: self.command("worker-once")),
            ("Восстановить очередь", lambda: self.command("recover")),
            ("Открыть Anime Factory V19", lambda: self.open_html(V19)),
            ("Открыть Anime Factory V20 Story & Combat", lambda: self.open_html(V20_STORY)),
            ("Открыть Anime Factory V21 Visual Quality", lambda: self.open_html(V21_VISUAL)),
            ("Открыть Anime Factory V22 Acting & Combat", lambda: self.open_html(V22_ACTING)),
            ("Открыть Anime Factory V23 Character Quality", lambda: self.open_html(V23_CHARACTER)),
            ("Открыть Anime Factory V24 Character Animation", lambda: self.open_html(V24_ANIMATION)),
            ("Открыть Anime Factory V25 Combat Choreography", lambda: self.open_html(V25_COMBAT)),
            ("Открыть Anime Factory V26 Cinematic Combat", lambda: self.open_html(V26_CINEMA)),
            ("Открыть Anime Factory V27 World Quality", lambda: self.open_html(V27_WORLD)),
            ("Открыть Anime Factory V28 Character World Interaction", lambda: self.open_html(V28_INTERACTION)),
            ("Открыть Anime Factory V29 Animation Combat Polish", lambda: self.open_html(V29_POLISH)),
            ("Открыть Anime Factory V30 Unified Quality Review", lambda: self.open_html(V30_REVIEW)),
            ("Открыть Anime Factory V31 Visual Production Review", lambda: self.open_html(V31_VISUAL)),
            ("Открыть Anime Factory V32 Keyframe Readability", lambda: self.open_html(V32_KEYFRAMES)),
            ("Открыть Anime Factory V33 Acting Expression", lambda: self.open_html(V33_ACTING)),
            ("Открыть Anime Factory V34 Storyboard Shot Continuity", lambda: self.open_html(V34_STORYBOARD)),
            ("Открыть Anime Factory V35 Scene Assembly", lambda: self.open_html(V35_ASSEMBLY)),
            ("Открыть Anime Factory V36 Audio & Episode Export", lambda: self.open_html(V36_AUDIO)),
            ("Открыть Anime Factory V37 Subtitles Delivery", lambda: self.open_html(V37_SUBTITLES)),
            ("Открыть Anime Factory V38 Cinematic Finishing", lambda: self.open_html(V38_CINEMA)),
            ("Открыть Anime Factory V39 Character Performance", lambda: self.open_html(V39_ACTION)),
            ("Открыть Anime Factory V40 Character Art", lambda: self.open_html(V40_ART)),
            ("Открыть Anime Factory V41 Silhouette Studio", lambda: self.open_html(V41_SILHOUETTES)),
            ("Открыть Anime Factory V42 Stage Lighting", lambda: self.open_html(V42_STAGE)),
            ("Открыть Anime Factory V43 Action Camera", lambda: self.open_html(V43_DIRECTOR)),
            ("Открыть Anime Factory V44 True Keyposes", lambda: self.open_html(V44_KEYPOSES)),
            ("Открыть Anime Factory V45 Art Engine", lambda: self.open_html(V45_ART_ENGINE)),
            ("Открыть Anime Factory V46 Animation Engine", lambda: self.open_html(V46_ANIMATION)),
            ("Открыть Anime Factory V47 Portable Voice", lambda: self.open_html(V47_VOICE)),
            ("Открыть Anime Factory V48 Episode Production", lambda: self.open_html(V48_EPISODE)),
            ("Открыть Anime Factory V20.3", lambda: self.open_html(V20)),
            ("Открыть папку проекта", self.show_workspace)
        ]
        for i, (label, fn) in enumerate(entries):
            button = ttk.Button(buttons, text=label, command=fn)
            button.grid(row=i // 3, column=i % 3, padx=4, pady=5, sticky="ew")
        for col in range(3):
            buttons.columnconfigure(col, weight=1)

        ttk.Label(win, text="Журнал действий", font=("Segoe UI", 11, "bold")).pack(
            anchor="w", padx=16, pady=(5, 0))
        self.log = scrolledtext.ScrolledText(win, height=15, wrap="word", font=("Consolas", 10))
        self.log.pack(fill="both", expand=True, padx=12, pady=9)
        self.write("V7 — автономный режим. ИИ-код не запускается автоматически.\n"
                   "Проверка и восстановление не требуют подключения к ChatGPT.\n")

    def write(self, value):
        self.log.insert("end", value + "\n")
        self.log.see("end")

    def command(self, action, *args):
        if self.busy:
            messagebox.showinfo("Задание выполняется", "Дождитесь завершения предыдущего задания.")
            return
        if not V7.is_file():
            messagebox.showerror("Нет движка", "Файл rescue-engine/unified_v7.py отсутствует.")
            return
        self.busy = True
        project = self.project.get().strip() or "default"
        argv = [sys.executable, str(V7), "--home", str(BASE), "--project", project,
                action, *map(str, args)]
        self.write("> " + action + " " + " ".join(map(str, args)))

        def run():
            try:
                process = subprocess.run(argv, cwd=BASE, capture_output=True, text=True,
                                         errors="replace", timeout=1800, shell=False)
                output = (process.stdout or "") + (process.stderr or "")
                code = process.returncode
            except Exception as exc:
                output, code = str(exc), 1
            self.win.after(0, lambda: self.done(code, output))

        threading.Thread(target=run, daemon=True).start()

    def done(self, code, output):
        self.busy = False
        self.write(output.rstrip() or "(Нет сообщений)")
        self.write("RESULT: " + ("PASS" if code == 0 else "ERROR " + str(code)) + "\n")

    def verify_bundle(self):
        filename = filedialog.askopenfilename(title="Выберите V7 ZIP",
                                              filetypes=[("ZIP", "*.zip")])
        if filename:
            self.command("bundle-verify", filename)

    def verify_project(self):
        filename = filedialog.askopenfilename(title="Выберите ZIP проекта",
                                              filetypes=[("ZIP", "*.zip")])
        if filename:
            self.command("verify", filename)

    def import_zip(self):
        filename = filedialog.askopenfilename(title="Импорт прежнего ZIP",
                                              filetypes=[("ZIP", "*.zip")])
        if filename:
            self.command("legacy-import", filename)

    def migrate(self):
        directory = filedialog.askdirectory(title="Старая папка files проекта V1-V6")
        if directory and messagebox.askyesno(
            "Подтверждение", "Скопировать файлы старого проекта, сохранив существующие?"
        ):
            self.command("migrate-files", directory)

    def enqueue(self):
        filename = filedialog.askopenfilename(title="JSON-задание",
                                              filetypes=[("JSON", "*.json")])
        if filename:
            self.command("queue", filename)

    def open_html(self, path):
        if not path.is_file():
            messagebox.showwarning("Нет HTML", "Файл не включён в эту сборку: " + str(path))
        else:
            webbrowser.open(path.resolve().as_uri())

    def show_workspace(self):
        project = self.project.get().strip() or "default"
        path = BASE / "workspace" / project / "files"
        path.mkdir(parents=True, exist_ok=True)
        webbrowser.open(path.resolve().as_uri())


if __name__ == "__main__":
    window = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    Studio(window)
    window.mainloop()
