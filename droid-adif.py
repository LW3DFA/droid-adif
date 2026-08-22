#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =================================================================
# DROID-ADIF
# Archivo     : droid-adif.py
# Autor       : Fernando - LW3DFA
# Proyecto    : 
# Versión     : 1.3 Modern UI 2026
# Descripción : Convierte Log APRSDROID en un ADIF
# =================================================================

import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from datetime import datetime, timedelta
from PIL import Image, ImageTk

APP_TITLE = "APRSdroid LOG → ADIF"
DEFAULT_STATION = "LW3DFA"
DEFAULT_FREQ = "144.390"

class RoundedButton(tk.Canvas):
    """Botón vectorial con esquinas redondeadas sin bucles de redimensionamiento."""
    def __init__(self, parent, text, command, bg_parent, color_normal, color_hover, font_size=10, radius=10, height=36, **kwargs):
        super().__init__(parent, bg=bg_parent, highlightthickness=0, bd=0, height=height, cursor="hand2", **kwargs)
        
        self.text = text
        self.command = command
        self.bg_parent = bg_parent
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.radius = radius
        self.font_size = font_size
        self.current_color = color_normal

        self.bind("<Configure>", self._draw)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", lambda e: self.command())

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, fill):
        """Dibujo vectorial de un rectángulo redondeado en Canvas."""
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1, x2, y1 + r,
            x2, y2 - r,
            x2, y2, x2 - r, y2,
            x1 + r, y2,
            x1, y2, x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, fill=fill)

    def _draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        
        if w > 1 and h > 1:
            self._draw_rounded_rect(2, 2, w - 2, h - 2, self.radius, self.current_color)
            self.create_text(
                w / 2, h / 2,
                text=self.text,
                fill="#FFFFFF",
                font=("Segoe UI", self.font_size, "bold")
            )

    def _on_enter(self, event):
        self.current_color = self.color_hover
        self._draw()

    def _on_leave(self, event):
        self.current_color = self.color_normal
        self._draw()


def strip_ssid(callsign):
    if not callsign:
        return ""
    call = callsign.strip().upper().split("-", 1)[0]
    return re.sub(r'[^A-Z0-9]', '', call)

def parse_datetime_from_line(line):
    patterns = [
        (r"(\d{4}-\d{2}-\d{2})[\sT]+(\d{2}:\d{2}:\d{2})", "%Y-%m-%d %H:%M:%S"),
        (r"(\d{2}/\d{2}/\d{4})[\sT]+(\d{2}:\d{2}:\d{2})", "%d/%m/%Y %H:%M:%S"),
        (r"(\d{2}-\d{2}-\d{4})[\sT]+(\d{2}:\d{2}:\d{2})", "%d-%m-%Y %H:%M:%S"),
    ]
    for pattern, fmt in patterns:
        m = re.search(pattern, line)
        if m:
            d, t = m.groups()
            try:
                return datetime.strptime(f"{d} {t}", fmt)
            except ValueError:
                pass
    return None

def parse_aprs_line(line):
    text = line.strip()
    dt = parse_datetime_from_line(text)
    if not dt:
        return None
    
    direction = None
    parts = text.split('\t')
    for p in parts:
        if p.strip() in ["RX", "TX"]:
            direction = p.strip()
            break
            
    if not direction:
        upper = text.upper()
        if " TX " in f" {upper} " or " TX\t" in upper:
            direction = "TX"
        elif " RX " in f" {upper} " or " RX\t" in upper:
            direction = "RX"
        else:
            return None

    m = re.search(r'([A-Z0-9\-]+)>([A-Z0-9\-]+)', text, re.IGNORECASE)
    if not m:
        return None
        
    source, destination = m.group(1), m.group(2)
    
    msg_match = re.search(r'::([A-Z0-9\-]+)\s*:', text, re.IGNORECASE)
    if msg_match:
        target_station = msg_match.group(1).strip()
        if direction == "TX":
            destination = target_station
        elif direction == "RX":
            source = target_station

    return {
        "dt": dt,
        "direction": direction,
        "source": source,
        "destination": destination,
        "line": text,
    }

def adif_field(name, value):
    value = "" if value is None else str(value)
    return f"<{name}:{len(value)}>{value}"

def generate_adif(records, station_callsign, utc_offset, freq):
    station = strip_ssid(station_callsign)
    offset = timedelta(hours=utc_offset)
    
    contacts = {}

    for rec in records:
        source_raw = rec["source"]
        dest_raw = rec["destination"]
        
        sb = strip_ssid(source_raw)
        db = strip_ssid(dest_raw)

        if rec["direction"] == "RX" and db == station:
            contacts.setdefault(sb, []).append(("RX", rec["dt"], source_raw, rec["line"]))
        elif rec["direction"] == "TX" and sb == station:
            contacts.setdefault(db, []).append(("TX", rec["dt"], dest_raw, rec["line"]))

    candidates = []
    
    for call_base, events in contacts.items():
        if not call_base or call_base == station:
            continue
            
        events.sort(key=lambda x: x[1])
        first_event = events[0]
        ssid_full = first_event[2]
        
        local_dt = first_event[1]
        utc_dt = local_dt + offset

        candidates.append({
            "call": call_base,
            "ssid": ssid_full,
            "local_dt": local_dt,
            "utc_dt": utc_dt,
            "line": first_event[3]
        })

    candidates.sort(key=lambda q: q["utc_dt"])

    unique = []
    seen = set()
    for q in candidates:
        if q["call"] not in seen:
            seen.add(q["call"])
            unique.append(q)

    lines = ["ADIF_VER:3.1.4", "<PROG_ID>DROID-ADIF", "<PROGRAMO>Fernando LW3DFA ", "<EOH>"]
    for q in unique:
        dt = q["utc_dt"]
        fields = [
            adif_field("STATION_CALLSIGN", station),
            adif_field("QSO_DATE", dt.strftime("%Y%m%d")),
            adif_field("CALL", q["call"]),
            adif_field("TIME_ON", dt.strftime("%H%M")),
            adif_field("MODE", "APRS"),
        ]
        if freq:
            fields.append(adif_field("FREQ", freq))
            
        fields.append(adif_field("COMMENT", ""))
        fields.append("<EOR>")
        lines.append("".join(fields))

    return "\n".join(lines) + "\n", len(candidates), len(unique)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("580x680")  # Aumentado para acomodar la frecuencia
        self.root.resizable(False, False)
        
        self.bg_color = "#F8FAFC"
        self.card_bg = "#FFFFFF"
        self.primary = "#319C10"
        self.primary_hover = "#3FCC14"
        self.secondary = "#0E47C4"
        self.secondary_hover = "#334155"
        self.text_dark = "#0F172A"
        self.text_muted = "#64748B"
        self.border_color = "#E2E8F0"

        self.root.configure(bg=self.bg_color)
        
        self.log_path = tk.StringVar()
        self.station = tk.StringVar(value=DEFAULT_STATION)
        self.freq = tk.StringVar(value=DEFAULT_FREQ)
        self.utc_offset = tk.StringVar(value="+3")
        
        self.setup_styles()
        self.build_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=self.bg_color)
        style.configure("Header.TLabel", background=self.bg_color, foreground=self.text_dark,
                        font=("Segoe UI", 18, "bold"))
        style.configure("SubHeader.TLabel", background=self.bg_color, foreground=self.primary,
                        font=("Segoe UI", 10, "bold"))
        style.configure("FieldLabel.TLabel", background=self.bg_color, foreground=self.text_dark,
                        font=("Segoe UI", 9, "bold"))
        style.configure("Muted.TLabel", background=self.bg_color, foreground=self.text_muted,
                        font=("Segoe UI", 8))

        style.configure("TEntry", fieldbackground="#FFFFFF", foreground=self.text_dark,
                        bordercolor=self.border_color, lightcolor=self.border_color,
                        darkcolor=self.border_color, padding=6)
        
        style.configure("TCombobox", fieldbackground="#FFFFFF", foreground=self.text_dark,
                        bordercolor=self.border_color, padding=4)

    def build_ui(self):
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill="both", expand=True)

        # Header / Título Principal + Logo
        header_frame = ttk.Frame(main)
        header_frame.pack(fill="x", pady=(0, 15))

        text_frame = ttk.Frame(header_frame)
        text_frame.pack(side="left", fill="both", expand=True)

        ttk.Label(text_frame, text="APRSdroid LOG → ADIF", style="Header.TLabel").pack(anchor="w")
        ttk.Label(text_frame, text="by Fernando LW3DFA", style="SubHeader.TLabel").pack(anchor="w")

        logo_path = Path("logo.png")
        if logo_path.exists():
            try:
                img = Image.open(logo_path).convert("RGBA")
                img = img.resize((85, 85), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                
                logo_label = tk.Label(
                    header_frame, 
                    image=self.logo_img, 
                    bg=self.bg_color,
                    bd=0,
                    highlightthickness=0
                )
                logo_label.pack(side="right", padx=(10, 0))
            except Exception as e:
                print(f"No se pudo cargar el logo: {e}")

        ttk.Separator(main, orient="horizontal").pack(fill="x", pady=(0, 15))

        # Archivo LOG
        ttk.Label(main, text="Archivo LOG de APRSdroid:", style="FieldLabel.TLabel").pack(anchor="w", pady=(0, 4))
        ff = ttk.Frame(main)
        ff.pack(fill="x", pady=(0, 12))
        ttk.Entry(ff, textvariable=self.log_path).pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        btn_select = RoundedButton(
            ff, "Seleccionar...", self.select_log, self.bg_color, self.secondary, self.secondary_hover, font_size=9, radius=8, height=32, width=110
        )
        btn_select.pack(side="right")

        # Container horizontal para Indicativo y Frecuencia
        grid_frame = ttk.Frame(main)
        grid_frame.pack(fill="x", pady=(0, 12))

        # Indicativo de Estación (Columna Izquierda)
        station_frame = ttk.Frame(grid_frame)
        station_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Label(station_frame, text="Indicativo de la estación:", style="FieldLabel.TLabel").pack(anchor="w", pady=(0, 4))
        ttk.Entry(station_frame, textvariable=self.station).pack(fill="x")

        # Frecuencia (Columna Derecha)
        freq_frame = ttk.Frame(grid_frame)
        freq_frame.pack(side="right", fill="x", expand=True)
        ttk.Label(freq_frame, text="Frecuencia (MHz):", style="FieldLabel.TLabel").pack(anchor="w", pady=(0, 4))
        
        freq_combo = ttk.Combobox(
            freq_frame, 
            textvariable=self.freq, 
            values=["144.390", "144.800", "145.825", "430.930"],
            width=15
        )
        freq_combo.pack(fill="x")

        # Zona Horaria / UTC
        ttk.Label(main, text="Diferencia horaria respecto a UTC:", style="FieldLabel.TLabel").pack(anchor="w", pady=(0, 4))
        uf = ttk.Frame(main)
        uf.pack(anchor="w", pady=(0, 2))
        ttk.Entry(uf, textvariable=self.utc_offset, width=8).pack(side="left", padx=(0, 8))
        ttk.Label(uf, text="horas (Argentina: +3)", style="Muted.TLabel").pack(side="left")
        
        ttk.Label(
            main,
            text="Ejemplo: 22:35 local +3 = 01:35 UTC (día siguiente). El cambio de día se calcula automáticamente.",
            style="Muted.TLabel",
            wraplength=520
        ).pack(anchor="w", pady=(0, 18))

        # Botón Generar ADIF
        btn_gen = RoundedButton(
            main, "⚡ GENERAR ADIF", self.generate, self.bg_color, self.primary, self.primary_hover, font_size=10, radius=10, height=40
        )
        btn_gen.pack(fill="x", pady=(0, 15))

        # Panel de Salida / Resultados
        ttk.Label(main, text="Resultado del Proceso:", style="FieldLabel.TLabel").pack(anchor="w", pady=(0, 6))
        
        self.result = tk.Text(
            main,
            height=8,
            width=65,
            state="disabled",
            wrap="word",
            bg="#0F172A",
            fg="#F1F5F9",
            insertbackground="#FFFFFF",
            selectbackground="#334155",
            font=("Consolas", 9),
            padx=10,
            pady=10,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.border_color
        )
        self.result.pack(fill="both", expand=True)

    def select_log(self):
        path = filedialog.askopenfilename(
            title="Seleccionar LOG de APRSdroid",
            filetypes=[("Logs APRSdroid", "*.log"), ("Todos los archivos", "*.*")]
        )
        if path:
            self.log_path.set(path)

    def show_result(self, text):
        self.result.config(state="normal")
        self.result.delete("1.0", "end")
        self.result.insert("1.0", text)
        self.result.config(state="disabled")

    def generate(self):
        path_text = self.log_path.get().strip()
        station = self.station.get().strip()
        freq = self.freq.get().strip().replace(",", ".")
        
        if not path_text:
            messagebox.showwarning(APP_TITLE, "Seleccioná primero un archivo LOG.")
            return
        if not station:
            messagebox.showwarning(APP_TITLE, "Ingresá el indicativo de la estación.")
            return
        try:
            utc_offset = float(self.utc_offset.get().strip().replace(",", "."))
        except ValueError:
            messagebox.showerror(APP_TITLE, "La diferencia horaria debe ser un número. Ejemplos: +3, -3, 0")
            return

        path = Path(path_text)
        if not path.exists():
            messagebox.showerror(APP_TITLE, "El archivo seleccionado no existe.")
            return

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            records = []
            for line in content.splitlines():
                parsed = parse_aprs_line(line)
                if parsed:
                    records.append(parsed)

            if not records:
                messagebox.showwarning(
                    APP_TITLE,
                    "No se encontraron líneas APRS reconocibles con fecha/hora y dirección RX/TX."
                )
                return

            adif, found, unique = generate_adif(records, station, utc_offset, freq)
            output_path = path.with_suffix(".adi")
            output_path.write_text(adif, encoding="utf-8")
            qso_count = adif.count("<EOR>")

            freq_str = f"{freq} MHz" if freq else "No especificada"
            result = (
                f"LOG ANALIZADO EXITOSAMENTE\n{'─' * 42}\n"
                f"Archivo: {path.name}\n"
                f"Indicativo Estación: {strip_ssid(station)}\n"
                f"Frecuencia: {freq_str}\n"
                f"Ajuste UTC: +{utc_offset:g} hs\n\n"
                f"Líneas válidas parseadas: {len(records)}\n"
                f"QSOs únicos exportados: {qso_count}\n\n"
                f"Archivo ADIF generado:\n{output_path.name}\n\n"
                f"Ubicación:\n{output_path}"
            )
            self.show_result(result)
            messagebox.showinfo(
                APP_TITLE,
                f"ADIF generado correctamente.\n\nQSOs: {qso_count}\nFrecuencia: {freq_str}\nArchivo: {output_path.name}"
            )
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"Ocurrió un error al procesar el LOG:\n\n{exc}")

def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()