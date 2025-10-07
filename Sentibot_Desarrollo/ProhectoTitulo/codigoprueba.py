from fpdf import FPDF
import subprocess

# ==== Obtener log de git ====
# Formato: hash, autor, fecha, mensaje separado por ----
git_log = subprocess.check_output(
    ["git", "log", "--pretty=format:%H%n%an%n%ad%n%s%n----", "--date=short"], text=True
)

# ==== Crear PDF ====
pdf = FPDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

# ===== Título =====
pdf.set_font("Arial", 'B', 16)
pdf.set_text_color(0, 0, 128)
pdf.cell(0, 10, "Historial de Commits del Proyecto", 0, 1, 'C')
pdf.ln(5)

# ===== Configuración de fuente para commits =====
pdf.set_font("Arial", '', 12)

# Separar commits y agregarlos al PDF
commits = git_log.split("----")
for commit in commits:
    lines = commit.strip().split("\n")
    if len(lines) >= 4:
        commit_hash, author, date, message = lines[:4]
        
        # Hash del commit en azul
        pdf.set_text_color(0, 0, 180)
        pdf.set_font("Arial", 'B', 12)
        pdf.multi_cell(0, 6, f"Commit: {commit_hash}")
        
        # Autor y fecha en verde
        pdf.set_text_color(0, 128, 0)
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 6, f"Autor: {author}   Fecha: {date}")
        
        # Mensaje en negro
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, f"Mensaje: {message}")
        
        pdf.ln(4)  # Espacio entre commits

# Guardar PDF
pdf.output("Git_Log.pdf")
print("PDF generado con éxito: Git_Log.pdf")
