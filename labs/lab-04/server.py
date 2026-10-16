# AI-assisted comments: expanded from the student's summary; review for understanding.
# This file runs the FastAPI server for the flashcard application.
# It receives notes from the client and checks the request using Pydantic.
# Then it sends the notes to the AI flashcard generator and returns
# the generated flashcards as JSON.
# It also handles browser cross-origin access, measures server processing time,
# and reports errors if something goes wrong.
# The assignment asks for student-written comments. Review these explanations
# and express them in your own words before submitting.



# Uvicorn runs the HTTP server; time supplies the clock for duration measurement.
import uvicorn
import time
# FastAPI builds the app, HTTPException creates HTTP errors, and Request describes
# the incoming HTTP request passed to the timing middleware.
from fastapi import FastAPI, HTTPException, Request
# CORS handles browser cross-origin permissions, not authentication.
from fastapi.middleware.cors import CORSMiddleware
# BaseModel is Pydantic's base class for validated data models.
from pydantic import BaseModel

# Import the async generator that returns validated flashcards.
from flashcard_generator import generate_flashcards

# Create the app on which middleware and routes are registered.
app = FastAPI()

# Allow browser requests from all origins, methods, and request headers.
# A deployed application would normally use more restricted origin settings.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wrap HTTP processing and add its server-side duration in seconds to the response.
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    # Let the remaining app process the request; yield while its async work waits.
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# FastAPI validates the JSON body against this model before entering the route.
# notes is required; cards defaults to 3. Compatible values may be converted.
# Blank notes and card-count limits are checked by the generator, not this model.
class GenerateRequest(BaseModel):
    notes: str
    cards: int = 3

# Handle POST requests with notes and an optional card count.
@app.post("/api/generate")
async def generate_cards(request: GenerateRequest):
    try:
        # Await generation; FastAPI serializes the returned Pydantic object as JSON.
        result = await generate_flashcards(request.notes, request.cards)
        return result
    except Exception as e:
        # Preserve the supplied behavior: log the error and return HTTP 500 details.
        # The generator sanitizes provider errors; raw exceptions here could leak data.
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run Uvicorn only for direct execution, not when tests import this module.
if __name__ == "__main__":
    print("Server running on http://localhost:3000")
    # Bind all network interfaces on port 3000; the client uses localhost.
    uvicorn.run(app, host="0.0.0.0", port=3000)
