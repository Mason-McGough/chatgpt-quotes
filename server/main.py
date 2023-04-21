import csv
from string import Template
import random

import yaml
import tomli
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class QuoteResponse(BaseModel):
    """
    Response format from request.
    """
    quote: str | None
    author: str | None


# Load variables from pyproject.toml
with open("pyproject.toml", mode="rb") as fp:
    config = tomli.load(fp)

__version__ = config["tool"]["poetry"]["version"]
DESCRIPTION = config["tool"]["poetry"]["description"]
TITLE = config["app"]["title"]
PLUGIN_HOSTNAME = config["app"]["plugin_hostname"]
PORT = config["app"]["port"]
QUOTES_FILE = config["app"]["quotes_file"]


def parse_quotes(filepath: str) -> list[tuple[str, str, str]]:
    """
    Parse quotes from a CSV file.
    
    Each line is in format "QUOTE;AUTHOR;GENRE"
    """

    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        quotes = []
        for row in reader:
            quote, author, genre = row
            quotes.append((quote, author, genre))
        return quotes


# Create a FastAPI application to interface with ChatGPT
main_app = FastAPI(
    title=TITLE,
    description=DESCRIPTION,
    version=__version__
)

# Add CORS middleware to enable ChatGPT to access ai-plugin.json
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount a static directory (for logo)
main_app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up required files in .well-known directory
@main_app.get("/.well-known/ai-plugin.json")
async def get_ai_plugin(request: Request) -> Response:
    """
    Serve ai-plugin.json file.
    """

    # Read raw ai-plugin.json from file
    with open("ai-plugin.json", "r") as f:
        content_str = f.read()

    # Replace string placeholders with their values (while preserving other instances of $)
    content_str = Template(content_str).safe_substitute(PLUGIN_HOSTNAME=PLUGIN_HOSTNAME)

    # Return string as Response
    return Response(content=content_str, media_type="text/plain")

@main_app.get("/openapi.yaml", include_in_schema=False)
async def get_openapi_yaml(request: Request) -> Response:
    """
    Serve openapi.yaml file.
    """

    # Get openapi data from chat_app (we only care about ChatGPT-facing endpoints)
    openapi_data = main_app.openapi()

    # Fill in missing server urls field with hostname
    openapi_data["info"]["servers"] = [PLUGIN_HOSTNAME]

    # Return as yaml-formatted Response
    openapi_yaml = yaml.dump(openapi_data)
    return Response(content=openapi_yaml, media_type="text/plain")

@main_app.on_event("startup")
async def startup():
    """
    Executed when startup event is triggered to do setup.
    """
    global QUOTES
    QUOTES = parse_quotes(QUOTES_FILE)

@main_app.get(
    "/quotes/random",
    response_model=QuoteResponse,
    description="Get a random quote. If an author is requested, return a random quote from that author."
)
async def random_quote(
    request: Request,
    author: str | None = None
) -> QuoteResponse:
    """
    Randomly select a quote from pool of quotes.
    """

    if author:
        all_quotes = [q for q in QUOTES if q[1].lower() == author.lower()]
    else:
        all_quotes = QUOTES

    if len(all_quotes) > 0:
        quote, author, _ = random.choice(all_quotes)
        return QuoteResponse(quote=quote, author=author)
    else:
        return QuoteResponse(quote=None, author=None)

def start():
    """
    Start server.
    """
    uvicorn.run("server.main:main_app", host="0.0.0.0", port=PORT, reload=True)
