import os
import subprocess

def get_download_info(url):
    # 1. Check for new format: *.mpd*KID:KEY
    if ".mpd" in url and "*" in url:
        parts = url.split("*", 1)
        if len(parts) == 2:
            clean_url = parts[0].strip()
            key_data = parts[1].strip()
            if ":" in key_data:
                kid, key = key_data.split(":", 1)
                # Return clean URL and formatted key string for N_m3u8DL-RE
                return clean_url, f"--key {kid.strip()}:{key.strip()}"
    
    # 2. Fallback for old format: #keysV1=
    if "#keysV1=" in url:
        url_clean = url.split("#keysV1=")[0]
        keys_part = url.split("#keysV1=")[1]
        return url_clean, keys_part
        
    return url, ""

async def download_video_with_nre(mpd, keys_string, name):
    os.makedirs("downloads", exist_ok=True)
    
    # Define output path
    output_file = f"downloads/{name}.mp4"
    
    if keys_string:
        # Use N_m3u8DL-RE for DRM decryption
        # -mt enables multi-threading for faster download
        cmd = f'N_m3u8DL-RE "{mpd}" {keys_string} --save-name "{name}" --tmp-dir downloads --save-dir downloads -mt'
        print(f"🚀 Running N_m3u8DL-RE: {cmd}")
    else:
        # Fallback to yt-dlp for non-DRM content
        cmd = f'yt-dlp -o "{output_file}" "{mpd}"'
        print(f"🚀 Running yt-dlp: {cmd}")
    
    # Execute command
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3600) # 1 hour timeout
        
        # Check if .mp4 was created successfully
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            print(f"✅ Download Success: {output_file}")
            return output_file
            
        # Sometimes NRE saves as .mkv even if we asked for mp4, check that too
        mkv_file = f"downloads/{name}.mkv"
        if os.path.exists(mkv_file) and os.path.getsize(mkv_file) > 0:
            print(f"✅ Download Success (MKV): {mkv_file}")
            return mkv_file
            
        print(f"❌ Download Failed. Stderr: {result.stderr[-500:]}")
        return None
    except Exception as e:
        print(f"❌ Error during download execution: {e}")
        return None
