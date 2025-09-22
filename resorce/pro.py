import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import threading
import yt_dlp
import shutil
import os

def choose_cookie_file():
    paths = filedialog.askopenfilenames(title="انتخاب فایل‌های کوکی", filetypes=[("Text files","*.txt"),("All files","*.*")])
    if paths:
        cookies_entry.delete(0, tk.END)
        cookies_entry.insert(0, ";".join(paths))

def start_download():
    urls = [entry.get().strip() for entry in url_entries if entry.get().strip()]
    if not urls:
        messagebox.showerror("خطا", "حداقل یک لینک وارد کنید")
        return

    folder = filedialog.askdirectory(title="پوشه ذخیره ویدیوها را انتخاب کنید")
    if not folder:
        return

    cookies_text = cookies_entry.get().strip()
    cookies_list = [c.strip() for c in cookies_text.replace("\n",";").split(";") if c.strip()]

    selected_quality = quality_var.get()

    # اگر کیفیت انتخاب‌شده نیاز به ffmpeg دارد ولی نصب نشده، خطا بده
    if selected_quality in ("1080p","720p","480p","audio") and not shutil.which("ffmpeg"):
        messagebox.showerror("خطا", "این کیفیت نیاز به ffmpeg دارد.\nلطفاً ffmpeg نصب کنید یا کیفیت 'best' انتخاب کنید.")
        return

    for i, url in enumerate(urls):
        progress_bars[i]['value'] = 0
        status_labels[i].config(text="در حال دانلود...", fg="blue")
        threading.Thread(
            target=download_video, 
            args=(url, cookies_list, folder, progress_bars[i], status_labels[i], selected_quality)
        ).start()

def download_video(url, cookies_list, download_folder, progress_bar, status_label, quality):
    last_error = None
    for i, cf in enumerate(cookies_list if cookies_list else [""]):
        try:
            def progress_hook(d):
                if d['status'] == 'downloading':
                    try:
                        percent = float(d['_percent_str'].replace('%', '').strip())
                        progress_bar['value'] = percent
                    except:
                        pass
                elif d['status'] == 'finished':
                    progress_bar['value'] = 100
                    status_label.config(text="در حال پردازش...", fg="orange")

            ydl_opts = {
                'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'quiet': True,
                'no_warnings': True
            }

            # انتخاب کیفیت
            if quality == "best":
                ydl_opts['format'] = "best"
            elif quality == "1080p":
                ydl_opts['format'] = "bestvideo[height<=1080]+bestaudio"
            elif quality == "720p":
                ydl_opts['format'] = "bestvideo[height<=720]+bestaudio"
            elif quality == "480p":
                ydl_opts['format'] = "bestvideo[height<=480]+bestaudio"
            elif quality == "audio":
                ydl_opts['format'] = "bestaudio/best"
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]

            if cf:
                ydl_opts['cookiefile'] = cf

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            status_label.config(text="دانلود کامل شد ✅", fg="green")
            return
        except Exception as e:
            last_error = e
            continue
    status_label.config(text="دانلود ناموفق ❌", fg="red")
    messagebox.showerror("خطا", f"دانلود با همه کوکی‌ها ناموفق بود:\n{last_error}")

# رابط کاربری
root = tk.Tk()
root.title("دانلودر یوتیوب با انتخاب کیفیت")
root.geometry("650x400")
root.configure(bg="#f0f0f0")

tk.Label(root, text="لینک‌ها:", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=10)

url_entries = []
progress_bars = []
status_labels = []

frame = tk.Frame(root, bg="#f0f0f0")
frame.pack()

for i in range(5):
    tk.Label(frame, text=f"لینک {i+1}:", bg="#f0f0f0").grid(row=i, column=0, padx=5, pady=5)
    entry = tk.Entry(frame, width=50)
    entry.grid(row=i, column=1, padx=5, pady=5)
    url_entries.append(entry)

    pb = ttk.Progressbar(frame, orient="horizontal", length=200, mode="determinate")
    pb.grid(row=i, column=2, padx=5, pady=5)
    progress_bars.append(pb)

    status = tk.Label(frame, text="", bg="#f0f0f0")
    status.grid(row=i, column=3, padx=5, pady=5)
    status_labels.append(status)

# انتخاب کیفیت
quality_frame = tk.Frame(root, bg="#f0f0f0")
quality_frame.pack(pady=10)
tk.Label(quality_frame, text="کیفیت:", bg="#f0f0f0").pack(side="left", padx=5)
quality_var = tk.StringVar(value="best")
quality_combo = ttk.Combobox(quality_frame, textvariable=quality_var, values=["best","1080p","720p","480p","audio"], width=10)
quality_combo.pack(side="left")

tk.Label(root, text="فایل کوکی‌ها (جدا شده با ;):", bg="#f0f0f0").pack(pady=5)
cookies_entry = tk.Entry(root, width=60)
cookies_entry.pack()
tk.Button(root, text="انتخاب فایل کوکی", command=choose_cookie_file).pack(pady=5)

download_btn = tk.Button(root, text="دانلود همه ویدیوها", command=start_download, bg="green", fg="white", font=("Arial", 12, "bold"))
download_btn.pack(pady=10)

root.mainloop()
