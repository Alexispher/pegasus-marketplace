import subprocess
import threading
import customtkinter as ctk

PLUGIN_NAME = 'Node.js V8 Engine'
SUPPORTED_EXT = '.js'

def execute(filepath, area):
    ctk.CTkLabel(area, text=f"🟢 Running Node.js: {filepath.split('/')[-1]}", font=("Arial", 16, "bold"), text_color="#2ecc71").pack(pady=(20, 10))
    
    output_frame = ctk.CTkScrollableFrame(area, fg_color="#1e1e1e", border_width=1, border_color="#333")
    output_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def run_script():
        try:
            process = subprocess.Popen(
                ['node', filepath], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                encoding='utf-8'
            )

            for line in iter(process.stdout.readline, ''):
                if line:
                    area.after(0, lambda l=line.strip(): ctk.CTkLabel(output_frame, text=l, font=("Consolas", 13), text_color="#cccccc", anchor="w").pack(fill="x"))

            for err_line in iter(process.stderr.readline, ''):
                if err_line:
                    area.after(0, lambda l=err_line.strip(): ctk.CTkLabel(output_frame, text=l, font=("Consolas", 13), text_color="#e74c3c", anchor="w").pack(fill="x"))

            process.stdout.close()
            process.stderr.close()
            process.wait()

            area.after(0, lambda: ctk.CTkLabel(output_frame, text="\n[Process finished successfully]", font=("Consolas", 12, "italic"), text_color="#f1c40f", anchor="w").pack(fill="x", pady=10))

        except FileNotFoundError:
            area.after(0, lambda: ctk.CTkLabel(output_frame, text="FATAL ERROR: 'node' command not found. Ensure Node.js is installed.", text_color="#e74c3c").pack())
        except Exception as e:
            area.after(0, lambda: ctk.CTkLabel(output_frame, text=f"Engine Error: {str(e)}", text_color="#e74c3c").pack())

    threading.Thread(target=run_script, daemon=True).start()