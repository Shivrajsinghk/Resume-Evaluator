# Resume Evaluator

An LLM-powered mini project that evaluates resumes against a backend engineering job description. It extracts structured information from each resume, compares the candidate with the role, assigns a match score, and prints the candidates in descending order of fit.

The project uses the [Groq](https://groq.com/) API with `openai/gpt-oss-20b`, [Pydantic](https://docs.pydantic.dev/) for structured validation, and PDF/DOCX parsers for reading resumes.

## Features

- Reads resumes in `.pdf` and `.docx` format
- Extracts structured resume data, including:
  - Candidate name and contact information
  - Total experience
  - Skills
  - Work experience and internships
  - Education, projects, and certifications
- Extracts structured requirements from the job description
- Compares every resume with the job requirements
- Reports matching skills, missing skills, experience fit, a match percentage, and a short verdict
- Sorts candidates from highest to lowest score

## Project structure

```text
Resume-Evaluator/
|-- Resume-Evaluator.py       # Main evaluation script
|-- resumes/                  # Input resumes
|   |-- Aarav_Mehta.pdf
|   |-- Daniel_Brooks.pdf
|   `-- ...
`-- README.md
```

## Requirements

- Python 3.10 or newer
- A Groq API key
- Resume files in PDF or DOCX format

## Installation

From the `Resume-Evaluator` directory, create and activate a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install groq pypdf python-docx python-dotenv pydantic
```

## Configuration

Create a `.env` file inside the `Resume-Evaluator` directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

The script loads this value using `python-dotenv`. Do not commit `.env` or expose your API key in source control.

## Usage

1. Place `.pdf` or `.docx` resumes in the `resumes/` folder.
2. Open a terminal in the `Resume-Evaluator` directory.
3. Run the evaluator:

```bash
python Resume-Evaluator.py
```

The script processes each supported resume, sends the extracted content to the Groq API, and prints the final rankings.

## Example output

The exact output depends on the resumes and the model response, but it follows this general format:

```text
Processing the resume of Aarav_Mehta ...

{'score': 86, 'details': {
    'candidate_name': 'Aarav Mehta',
    'matching_skills': ['Python', 'microservices', 'Kafka'],
    'missing_important_skills': ['TypeScript'],
    'experience_requirement_met': True,
    'overall_match_percentage': 86,
    'final_verdict': 'Strong match for the Senior Backend Engineer role.'
}}
```

## How it works

1. The script scans the `resumes/` directory.
2. It extracts text from each PDF or DOCX file.
3. The LLM converts the resume text into a validated Pydantic model.
4. The job description is converted into structured requirements.
5. The LLM compares the structured resume and job requirements.
6. Results are collected, sorted by score, and printed.

## Customization

The job description is currently defined directly in `Resume-Evaluator.py`. To evaluate a different role, update the `job_description` string near the top of the file.

The model is configured with:

```python
model = 'openai/gpt-oss-20b'
```

You can replace this with another Groq-supported model if needed.

## Important notes

- This is an educational prototype, not an automated hiring decision system.
- LLM-generated scores can be inconsistent and should be reviewed by a qualified human.
- Resume content is sent to the configured Groq API; avoid using sensitive data without appropriate consent and safeguards.
- The script currently waits between API calls to reduce the chance of rate-limit errors.
- The `resumes/` path is relative, so run the script from the `Resume-Evaluator` directory.
- Scanned/image-only PDFs may not produce useful text unless OCR is added.

## Future improvements

- Accept the job description and resume directory as command-line arguments
- Export rankings to JSON or CSV
- Add retry handling and clearer API error messages
- Cache the parsed job description instead of parsing it for every resume
- Add OCR support for scanned resumes
- Add tests for document parsing and scoring behavior
- Build a web interface for uploading resumes and viewing results

## License

This project is intended for learning and experimentation. Add a license here if you plan to distribute it publicly.
