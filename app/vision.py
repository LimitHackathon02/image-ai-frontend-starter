from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from .images import image_data_uri
from .image_service import extract_image_text


def vision_router(engine):
    router = APIRouter()

    @router.post("/api/vision")
    async def vision(
        file: UploadFile = File(...),
        question: str = Form("사진에서 확인되는 정보와 다음 행동을 정리해줘.", min_length=1, max_length=2000),
        task: str = Form("image_analyze", max_length=80),
        use_cache: bool = Form(True),
    ):
        # 읽기 크기를 제한하며 UploadFile의 임시 스풀 파일도 항상 닫습니다.
        try:
            raw = await file.read(engine.settings.image_max_bytes + 1)
            if len(raw) > engine.settings.image_max_bytes:
                raise HTTPException(413, "이미지는 서버 용량 제한 이하로 업로드하세요.")
            image = await run_in_threadpool(image_data_uri, raw, engine.settings.image_max_pixels)
        finally:
            await file.close()
        if task == "image_text":
            return await extract_image_text(engine, image, cache=use_cache)
        return await engine.run(task, question, image=image, cache=use_cache)

    return router
