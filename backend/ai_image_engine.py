import base64
import io
import logging
from pathlib import Path
from typing import Dict, List

import numpy as np
import onnxruntime as ort
from PIL import Image

logger = logging.getLogger("password_breach_checker")


class ArcFaceEngine:
    def __init__(self, model_path: Path):
        self.model_path = model_path
        self.model_available = model_path.exists() and model_path.is_file() and model_path.stat().st_size > 0

    def _load_image(self, image_bytes: bytes) -> np.ndarray:
        with Image.open(io.BytesIO(image_bytes)) as img:
            return np.array(img.convert("RGB"))

    def _pseudo_embedding(self, img: np.ndarray) -> List[float]:
        reduced = img.mean(axis=(0, 1))
        normalized = reduced / (np.linalg.norm(reduced) + 1e-8)
        return normalized.tolist()

    def embed_from_bytes(self, image_bytes: bytes) -> Dict[str, object]:
        try:
            array = self._load_image(image_bytes)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to process image: %s", exc)
            return {"embeddings": [], "faces_detected": 0, "model": "unavailable", "error": str(exc)}

        if not self.model_available:
            pseudo = self._pseudo_embedding(array)
            logger.info("Returning pseudo embedding because model is missing")
            return {"embeddings": [pseudo], "faces_detected": 1, "model": "pseudo"}

        try:
            session = ort.InferenceSession(str(self.model_path), providers=["CPUExecutionProvider"])
            input_name = session.get_inputs()[0].name
            input_shape = session.get_inputs()[0].shape
            resized = np.array(Image.fromarray(array).resize((input_shape[2], input_shape[3])))
            normalized = resized.astype("float32") / 255.0
            normalized = np.transpose(normalized, (2, 0, 1))
            normalized = np.expand_dims(normalized, axis=0)
            outputs = session.run(None, {input_name: normalized})
            embedding = outputs[0].flatten().tolist()
            logger.info("Generated embedding with %s dimensions", len(embedding))
            return {"embeddings": [embedding], "faces_detected": 1, "model": "arcface"}
        except Exception as exc:  # noqa: BLE001
            logger.warning("ONNX model execution failed: %s", exc)
            pseudo = self._pseudo_embedding(array)
            return {"embeddings": [pseudo], "faces_detected": 1, "model": "pseudo", "error": str(exc)}


def process_image_base64(data: str, model_path: Path) -> Dict[str, object]:
    engine = ArcFaceEngine(model_path)
    try:
        image_bytes = base64.b64decode(data)
    except Exception as exc:  # noqa: BLE001
        logger.error("Unable to decode base64 image: %s", exc)
        return {"embeddings": [], "faces_detected": 0, "model": "unavailable", "error": "Invalid base64 data"}
    return engine.embed_from_bytes(image_bytes)
