# Test image: Python + XeLaTeX for the checklist PDF suite.
# Build from repo root:
#   docker build -f tests/Dockerfile -t checklist-editor-test .
#   docker run --rm checklist-editor-test

FROM python:3.12-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-xetex \
    texlive-fonts-recommended \
    fonts-paratype \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["pytest", "tests/test_latex_escape.py", "-q"]
