from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from io import BytesIO


@dataclass(frozen=True)
class ImageSimilarityDetail:
    score: float
    reasons: list[str]


def _download_image(url: str):
    import requests

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return BytesIO(response.content)


def _phash_similarity(image_stream_a, image_stream_b) -> float:
    from PIL import Image
    import imagehash

    image_a = Image.open(image_stream_a)
    image_b = Image.open(image_stream_b)
    hash_a = imagehash.phash(image_a)
    hash_b = imagehash.phash(image_b)
    distance = hash_a - hash_b
    max_distance = hash_a.hash.size
    return max(0.0, 1 - (distance / max_distance))


def _orb_similarity(image_stream_a, image_stream_b) -> float:
    import cv2
    import numpy as np

    image_a = cv2.imdecode(np.frombuffer(image_stream_a.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
    image_b = cv2.imdecode(np.frombuffer(image_stream_b.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
    if image_a is None or image_b is None:
        return 0.0

    orb = cv2.ORB_create()
    keypoints_a, descriptors_a = orb.detectAndCompute(image_a, None)
    keypoints_b, descriptors_b = orb.detectAndCompute(image_b, None)
    if descriptors_a is None or descriptors_b is None:
        return 0.0

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = matcher.match(descriptors_a, descriptors_b)
    if not matches:
        return 0.0

    good_matches = [match for match in matches if match.distance < 64]
    ratio = len(good_matches) / max(len(keypoints_a), len(keypoints_b), 1)
    return max(min(ratio, 1.0), 0.0)


def compare_images(url_a: str | None, url_b: str | None) -> ImageSimilarityDetail:
    if not url_a or not url_b:
        return ImageSimilarityDetail(score=0.0, reasons=["缺少圖樣連結"])

    reasons: list[str] = []

    if importlib.util.find_spec("PIL") is None or importlib.util.find_spec("imagehash") is None:
        return ImageSimilarityDetail(score=0.0, reasons=["缺少影像比對套件"])

    stream_a = _download_image(url_a)
    stream_b = _download_image(url_b)
    phash_score = _phash_similarity(stream_a, stream_b)
    score = phash_score

    if phash_score >= 0.85:
        reasons.append("圖樣感知哈希相似度高")

    if importlib.util.find_spec("cv2") is not None:
        stream_a.seek(0)
        stream_b.seek(0)
        orb_score = _orb_similarity(stream_a, stream_b)
        score = max(score, orb_score)
        if orb_score >= 0.6:
            reasons.append("圖樣ORB特徵相似")

    return ImageSimilarityDetail(score=score, reasons=reasons)
