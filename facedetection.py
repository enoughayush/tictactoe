"""Detect faces in photos, videos, or a webcam with OpenCV.

Install the dependency with:
    py -m pip install opencv-contrib-python

Examples:
    py facedetection.py photo.jpg
    py facedetection.py clip.mp4
    py facedetection.py --webcam
    py facedetection.py photo.jpg --known-faces known_faces

For recognition, put example images in one folder per person, for example:
known_faces/Alex/photo1.jpg
known_faces/Alex/photo2.jpg
known_faces/Sam/photo1.jpg
"""

import argparse
from pathlib import Path
import sys

try:
    import cv2
    import numpy as np
except ImportError as exc:
    raise SystemExit(
        "OpenCV is not installed. Install it with:\n"
        "  py -m pip install opencv-contrib-python"
    ) from exc

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}


def load_face_detector():
    """Load OpenCV's built-in Haar Cascade face detector."""
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(str(cascade_path))
    if detector.empty():
        raise RuntimeError(f"Could not load the Haar Cascade file: {cascade_path}")
    return detector


def train_face_recognizer(known_faces_folder: Path, detector):
    """Train LBPH using face photos stored in one folder per person."""
    if not hasattr(cv2, "face") or not hasattr(cv2.face, "LBPHFaceRecognizer_create"):
        raise RuntimeError(
            "Face recognition needs opencv-contrib-python. Install it with:\n"
            "  py -m pip install opencv-contrib-python"
        )
    if not known_faces_folder.is_dir():
        raise RuntimeError(f"Known-faces folder not found: {known_faces_folder}")

    samples = []
    labels = []
    names = {}
    image_extensions = IMAGE_EXTENSIONS

    for person_folder in sorted(known_faces_folder.iterdir()):
        if not person_folder.is_dir():
            continue
        person_label = len(names)
        person_samples = 0
        for image_path in person_folder.iterdir():
            if image_path.suffix.lower() not in image_extensions:
                continue
            image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            if image is None:
                print(f"Skipping unreadable image: {image_path}")
                continue
            faces = detector.detectMultiScale(
                image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            if len(faces) == 0:
                print(f"No face found in training image: {image_path}")
                continue

            # Use the largest detected face in each training photo.
            x, y, width, height = max(faces, key=lambda box: box[2] * box[3])
            face = image[y:y + height, x:x + width]
            face = cv2.resize(face, (200, 200))
            samples.append(cv2.equalizeHist(face))
            labels.append(person_label)
            person_samples += 1

        if person_samples:
            names[person_label] = person_folder.name
        else:
            print(f"No usable face images for {person_folder.name}; skipping this folder.")

    if not samples:
        raise RuntimeError(
            f"No faces could be trained from {known_faces_folder}. "
            "Add clear face photos to a subfolder for each person."
        )

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(samples, np.array(labels, dtype=np.int32))
    print(f"Trained recognition for {len(names)} person(s).")
    return recognizer, names


def annotate_frame(frame, detector, recognizer=None, names=None, threshold=70.0):
    """Draw face boxes and, when trained, predicted names on a video frame."""
    if names is None:
        names = {}
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    for x, y, width, height in faces:
        label = "Face detected"
        if recognizer is not None:
            face = gray[y:y + height, x:x + width]
            face = cv2.resize(face, (200, 200))
            face = cv2.equalizeHist(face)
            person_label, confidence = recognizer.predict(face)
            if confidence <= threshold:
                label = f"{names[person_label]} ({confidence:.0f})"
            else:
                label = "Unknown"

        cv2.rectangle(frame, (x, y), (x + width, y + height), (40, 210, 130), 2)
        cv2.putText(
            frame, label, (x, max(y - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX,
            0.65, (40, 210, 130), 2, cv2.LINE_AA,
        )
    return frame, len(faces)


def output_path_for(source: Path) -> Path:
    """Create a default output filename beside the input file."""
    return source.with_name(f"detected_{source.stem}{source.suffix}")


def process_image(source: Path, output: Path, detector, recognizer, names, threshold):
    image = cv2.imread(str(source))
    if image is None:
        raise RuntimeError(f"Could not open image: {source}")

    result, count = annotate_frame(image, detector, recognizer, names, threshold)
    if not cv2.imwrite(str(output), result):
        raise RuntimeError(f"Could not save the result to: {output}")
    print(f"Found {count} face(s). Saved the result to: {output}")
    cv2.imshow("Face Detection - press any key to close", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def process_video(source, output, detector, recognizer, names, threshold):
    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        raise RuntimeError(f"Could not open video source: {source}")

    writer = None
    if output is not None:
        fps = capture.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 25.0
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        codec = cv2.VideoWriter_fourcc(*("XVID" if output.suffix.lower() == ".avi" else "mp4v"))
        writer = cv2.VideoWriter(str(output), codec, fps, (width, height))
        if not writer.isOpened():
            capture.release()
            raise RuntimeError(f"Could not create output video: {output}")

    print("Video is running. Press Q in the video window to stop.")
    total_faces = 0
    while True:
        success, frame = capture.read()
        if not success:
            break
        result, count = annotate_frame(frame, detector, recognizer, names, threshold)
        total_faces += count
        if writer is not None:
            writer.write(result)
        cv2.imshow("Face Detection - press Q to stop", result)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    capture.release()
    if writer is not None:
        writer.release()
        print(f"Saved the processed video to: {output}")
    cv2.destroyAllWindows()
    print(f"Detected {total_faces} face(s) across the processed frames.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Detect faces in images, videos, or a webcam using OpenCV."
    )
    parser.add_argument("source", nargs="?", type=Path, help="Image or video file")
    parser.add_argument(
        "--webcam", nargs="?", type=int, const=0,
        help="Use the webcam (optionally choose a camera index, default: 0)",
    )
    parser.add_argument("--output", type=Path, help="Where to save the annotated result")
    parser.add_argument(
        "--known-faces", type=Path,
        help="Optional folder with one subfolder of example images per person",
    )
    parser.add_argument(
        "--threshold", type=float, default=70.0,
        help="LBPH recognition cutoff; lower is stricter (default: 70)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if (args.source is None) == (args.webcam is None):
        print("Choose either an image/video path or --webcam.", file=sys.stderr)
        return 2

    try:
        detector = load_face_detector()
        recognizer, names = (None, {})
        if args.known_faces:
            recognizer, names = train_face_recognizer(args.known_faces, detector)

        if args.webcam is not None:
            process_video(args.webcam, args.output, detector, recognizer, names, args.threshold)
        else:
            source = args.source
            if not source.is_file():
                raise RuntimeError(f"File not found: {source}")
            extension = source.suffix.lower()
            if extension in IMAGE_EXTENSIONS:
                output = args.output or output_path_for(source)
                process_image(source, output, detector, recognizer, names, args.threshold)
            elif extension in VIDEO_EXTENSIONS:
                output = args.output or output_path_for(source).with_suffix(".mp4")
                process_video(source, output, detector, recognizer, names, args.threshold)
            else:
                raise RuntimeError(f"Unsupported file type: {extension or '(no extension)'}")
    except (RuntimeError, cv2.error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

