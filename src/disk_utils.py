import csv
from pathlib import Path


def archive_message_csv(channel, message, file) -> bool:
    with Path(file).open("a", encoding="utf-8", newline="") as f:
        f_writer = csv.writer(f)
        f_writer.writerow(
            [
                message["timestamp"],
                channel["id"],
                channel["name"],
                message["id"],
                message["author"]["id"],
                message["author"]["username"],
                message["content"],
            ],
        )
    return True
