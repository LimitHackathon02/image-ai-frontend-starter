import base64
import io
import warnings

from fastapi import HTTPException
from PIL import Image, ImageOps, UnidentifiedImageError


def image_data_uri(raw, max_pixels=20_000_000):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(raw)) as original:
                if original.format not in {"PNG", "JPEG", "WEBP", "BMP"}:
                    raise ValueError("지원 형식 아님")
                if original.width * original.height > max_pixels:
                    raise HTTPException(413, "이미지 픽셀 수가 서버 제한을 초과합니다.")
                original.verify()
            with Image.open(io.BytesIO(raw)) as original:
                original.load()
                if original.width < 4 or original.height < 4:
                    raise ValueError("이미지는 가로·세로 4px 이상이어야 합니다.")
                image = ImageOps.exif_transpose(original).convert("RGB")
                image.thumbnail((1280, 1280))
                w, h = image.size
                # API의 5:1 비율 제한에 맞춰 흰 여백을 추가합니다.
                size = (max(w, (h+4)//5, 4), max(h, (w+4)//5, 4))
                image = ImageOps.pad(image, size, color="white") if size != image.size else image
                out = io.BytesIO()
                image.save(out, format="JPEG", quality=85)
                return "data:image/jpeg;base64," + base64.b64encode(out.getvalue()).decode()
    except (Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise HTTPException(413, "이미지 픽셀 수가 안전 제한을 초과합니다.") from None
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(422, "유효한 PNG/JPEG/WEBP/BMP 이미지를 사용하세요(최소 4px).") from None
