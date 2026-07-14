import os

def get_download_info(url):
    # 1. Pehle check karo ki kya URL mein .mpd aur * hai (New Format)
    if ".mpd" in url and "*" in url:
        parts = url.split("*", 1)
        if len(parts) == 2:
            clean_url = parts[0].strip()
            key_data = parts[1].strip()
            if ":" in key_data:
                kid, key = key_data.split(":", 1)
                # N_m3u8DL-RE ke liye formatted key return karo
                return clean_url, f"--key {kid.strip()}:{key.strip()}"
    
    # 2. Fallback: Purana #keysV1= format agar naya format na ho
    url_clean = url.split("#keysV1=")[0]
    keys_part = url.split("#keysV1=")[1] if "#keysV1=" in url else ""
    return url_clean, keys_part

async def download_video_with_nre(mpd, keys_string, name):
    # Ensure downloads directory exists
    os.makedirs("downloads", exist_ok=True)
    
    cmd = f'yt-dlp -o "downloads/{name}.mkv" "{mpd}"'
    if keys_string:
        # Agar keys hain, toh N_m3u8DL-RE use karo jo DRM decrypt karta hai
        cmd = f'N_m3u8DL-RE "{mpd}" {keys_string} --save-name "{name}" --tmp-dir downloads --save-dir downloads -mt'
    
    print(f"🚀 Running Download Command: {cmd}")
    os.system(cmd)
    
    filename = f"downloads/{name}.mkv"
    return filename if os.path.exists(filename) else None
