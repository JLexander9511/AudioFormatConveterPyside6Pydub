def human_size(bytes_count: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(bytes_count)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024

def _parse_ffmpeg_time(time_str: str) -> float:
    """
    Convierte una cadena time=HH:MM:SS.xx a segundos (float).
    """
    try:
        parts = time_str.strip().split(':')
        if len(parts) == 3:
            h = float(parts[0])
            m = float(parts[1])
            s = float(parts[2])
            return h * 3600 + m * 60 + s
    except Exception:
        pass
    return 0.0