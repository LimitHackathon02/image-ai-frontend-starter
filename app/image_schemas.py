from pydantic import BaseModel, ConfigDict


class ImageTextOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str
