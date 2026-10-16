"""The ACE card contract shared by the generator and HTTP client."""

from pydantic import BaseModel, ConfigDict, Field


class Flashcard(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    application: str = Field(min_length=1, description="A 1–2 sentence real-world scenario where the concept is used or required.")
    challenge: str = Field(min_length=1, description="A specific problem to solve in the application scenario.")
    answer: str = Field(min_length=1, description="The correct solution with a brief explanation; expand all acronyms.")
    evidence: str = Field(min_length=1, description="One continuous direct quotation copied exactly from the source notes, supporting the answer.")
    misconception: str = Field(min_length=1, description="A misconception written as a quoted statement a student might say.")
    correction: str = Field(min_length=1, description="Why the misconception is wrong, citing facts from the supplied notes.")


class FlashcardResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    flashcards: list[Flashcard] = Field(description="The requested list of ACE flashcards, grounded in the source notes.")
