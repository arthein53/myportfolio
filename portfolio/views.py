import mimetypes
import re
from pathlib import Path

from django.contrib.staticfiles import finders
from django.http import FileResponse, Http404, StreamingHttpResponse


_RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)$")


def _range_chunks(path, start, length, chunk_size=64 * 1024):
    with path.open("rb") as audio_file:
        audio_file.seek(start)
        remaining = length
        while remaining:
            chunk = audio_file.read(min(chunk_size, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk


def audio_file(request, filename):
    if Path(filename).name != filename or not filename.lower().endswith(".mp3"):
        raise Http404

    located = finders.find(f"audio/{filename}")
    if not located:
        raise Http404

    path = Path(located)
    size = path.stat().st_size
    content_type = mimetypes.guess_type(path.name)[0] or "audio/mpeg"
    range_match = _RANGE_RE.fullmatch(request.headers.get("Range", ""))

    if not range_match:
        response = FileResponse(path.open("rb"), content_type=content_type)
        response["Content-Length"] = str(size)
        response["Accept-Ranges"] = "bytes"
        return response

    start_text, end_text = range_match.groups()
    if start_text:
        start = int(start_text)
        end = min(int(end_text), size - 1) if end_text else size - 1
    elif end_text:
        suffix_length = min(int(end_text), size)
        start = size - suffix_length
        end = size - 1
    else:
        response = StreamingHttpResponse(status=416)
        response["Content-Range"] = f"bytes */{size}"
        return response

    if start >= size or start > end:
        response = StreamingHttpResponse(status=416)
        response["Content-Range"] = f"bytes */{size}"
        return response

    length = end - start + 1
    response = StreamingHttpResponse(
        _range_chunks(path, start, length),
        status=206,
        content_type=content_type,
    )
    response["Accept-Ranges"] = "bytes"
    response["Content-Length"] = str(length)
    response["Content-Range"] = f"bytes {start}-{end}/{size}"
    return response