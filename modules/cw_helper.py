import os
import subprocess

import re

def get_download_info(url):
    # 1. Check for kid/key query parameters in URL (e.g. url?kid=KID&key=KEY or url&kid=KID&key=KEY)
    if ".mpd" in url:
        kid_match = re.search(r"[?&]kid=([0-9a-fA-F\-]{32,36})", url)
        key_match = re.search(r"[?&]key=([0-9a-fA-F]{32})", url)
        if kid_match and key_match:
            kid = kid_match.group(1)
            key = key_match.group(1)
            # Clean URL by removing the kid/key query params
            clean_url = re.sub(r"[?&]kid=[0-9a-fA-F\-]{32,36}", "", url)
            clean_url = re.sub(r"[?&]key=[0-9a-fA-F]{32}", "", clean_url)
            # Clean up potential malformed query parameters like mpd&something or mpd?&something
            clean_url = re.sub(r"&+", "&", clean_url)
            clean_url = clean_url.replace(".mpd&", ".mpd?").rstrip("?&")
            return clean_url, f"--key {kid}:{key}"

    # 2. Check for new format: *.mpd*KID:KEY
    if ".mpd" in url and "*" in url:
        parts = url.split("*", 1)
        if len(parts) == 2:
            clean_url = parts[0].strip()
            key_data = parts[1].strip()
            if ":" in key_data:
                kid, key = key_data.split(":", 1)
                return clean_url, f"--key {kid.strip()}:{key.strip()}"
    
    # 3. Fallback for old format: #keysV1=
    url_clean = url.split("#keysV1=")[0]
    keys_part = url.split("#keysV1=")[1] if "#keysV1=" in url else ""
    return url_clean, keys_part

async def download_video_with_nre(mpd, keys_string, name):
    os.makedirs("downloads", exist_ok=True)
    
    # Define output path with .mp4 extension (Telegram prefers mp4)
    output_file = f"downloads/{name}.mp4"
    
    if keys_string:
        # Use N_m3u8DL-RE for DRM decryption
        cmd = f'N_m3u8DL-RE "{mpd}" {keys_string} --save-name "{name}" --tmp-dir downloads --save-dir downloads -mt'
        print(f"🚀 Running N_m3u8DL-RE: {cmd}")
    else:
        # Fallback to yt-dlp for non-DRM content
        cmd = f'yt-dlp -o "{output_file}" "{mpd}"'
        print(f"🚀 Running yt-dlp: {cmd}")
    
    # Execute command
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # Check if .mp4 was created successfully
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        print(f"✅ Download Success: {output_file}")
        return output_file
        
    # Sometimes NRE saves as .mkv even if we asked for mp4, check that too
    mkv_file = f"downloads/{name}.mkv"
    if os.path.exists(mkv_file) and os.path.getsize(mkv_file) > 0:
        print(f"✅ Download Success (MKV): {mkv_file}")
        return mkv_file
        
    print(f"❌ Download Failed. Stderr: {result.stderr[:200]}")
    return None
