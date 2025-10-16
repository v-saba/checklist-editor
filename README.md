# Checklist Generator

A web application that generates beautiful PDF checklists from user input. Built with Flask and LaTeX.

## Prerequisites

- Python 3.7+
- XeLaTeX (for PDF generation)
- Arial font (or modify the font in app.py)

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Enter your checklist details:
   - Title
   - Subtitle
   - Phases and items (follow the example format)

4. Click "Generate PDF" to download your checklist

## Features

- Modern, responsive UI
- Real-time PDF generation
- Support for multiple phases
- Clean, professional PDF output
- Checkbox-style items
- Customizable title and subtitle

## Customization

You can modify the LaTeX template in the `generate_latex()` function in `app.py` to change the PDF styling. 