
import cv2
import csv
import time
import os
from datetime import datetime

# Change this if OBS Virtual Camera uses a different device index.
CAMERA_INDEX = 1

OUTPUT_DIR = "obs_captured_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
video_path = os.path.join(OUTPUT_DIR, f"OBS_{run_id}.mp4")
csv_path = os.path.join(OUTPUT_DIR, f"OBS_{run_id}_frames.csv")

# DirectShow is often suitable for Windows camera capture.
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

if not cap.isOpened():
    raise RuntimeError(
        f"Could not open camera index {CAMERA_INDEX}. "
        "Try another index, such as 0, 2, or 3."
    )

# These are requested settings, not guaranteed actual values.
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
reported_fps = cap.get(cv2.CAP_PROP_FPS)

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(
    video_path, fourcc, 30.0, (width, height)
)

if not writer.isOpened():
    cap.release()
    raise RuntimeError("Could not create output video.")

print("Recording OBS Virtual Camera.")
print("Check the preview. Press Q to stop.")

frame_count = 0
start_time = time.perf_counter()
previous_time = None

try:
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        fields = [
            "run_id",
            "frame_number",
            "wall_clock_time",
            "elapsed_seconds",
            "inter_frame_interval_ms",
            "width",
            "height",
            "reported_camera_fps",
        ]
        log = csv.DictWriter(f, fieldnames=fields)
        log.writeheader()

        while True:
            ok, frame = cap.read()
            arrival = time.perf_counter()
            wall_time = datetime.now().isoformat(
                timespec="milliseconds"
            )

            if not ok:
                print("Frame read failed; stopping capture.")
                break

            elapsed = arrival - start_time
            interval_ms = (
                (arrival - previous_time) * 1000
                if previous_time is not None else None
            )

            writer.write(frame)

            log.writerow({
                "run_id": run_id,
                "frame_number": frame_count,
                "wall_clock_time": wall_time,
                "elapsed_seconds": round(elapsed, 6),
                "inter_frame_interval_ms": (
                    round(interval_ms, 3)
                    if interval_ms is not None else ""
                ),
                "width": frame.shape[1],
                "height": frame.shape[0],
                "reported_camera_fps": reported_fps,
            })

            frame_count += 1
            previous_time = arrival

            cv2.imshow("OBS Virtual Camera - Press Q to stop", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

finally:
    cap.release()
    writer.release()
    cv2.destroyAllWindows()


print("Capture finished.")
print("Frames captured:", frame_count)
print("Video saved to:", video_path)
print("Frame log saved to:", csv_path)
