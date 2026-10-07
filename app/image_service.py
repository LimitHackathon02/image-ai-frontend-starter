from .image_schemas import ImageTextOutput


async def extract_image_text(engine, image, cache=True):
    """공통 엔진의 제공자·모의 실행·예산·캐시를 재사용합니다."""
    result = await engine.run("image_text", "이미지의 글자를 원문 그대로 추출하세요.", image=image, cache=cache)
    result["output"] = ImageTextOutput.model_validate(result["output"]).model_dump()
    return result
