def get_download_info(url):
    url_clean = url.split("#keysV1=")[0]
    keys_part = url.split("#keysV1=")[1] if "#keysV1=" in url else ""
    return url_clean, keys_part

async def download_video_with_nre(mpd, keys_string, name):
    import os
    cmd = f'yt-dlp -o "{name}.mkv" "{mpd}"'
    if keys_string:
        cmd = f'N_m3u8DL-RE "{mpd}" {keys_string} --save-name "{name}" --tmp-dir downloads --save-dir downloads -mt'
    os.system(cmd)
    filename = f"{name}.mkv"
    return filename if os.path.exists(filename) else None
