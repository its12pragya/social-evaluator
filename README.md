# Social Media Post Evaluator

An AI-powered tool to evaluate LinkedIn, Instagram, and Substack posts using Chain-of-Thought prompting with Gemini 2.5 Flash.

## Features
- Platform-specific evaluation rubrics
- Dimension-by-dimension scoring (1-10)
- Actionable suggestions per dimension
- Rewrite suggestion for the weakest part

## Stack
- Python + Streamlit (local UI)
- Google Gemini 2.5 Flash API
- React + Lovable (deployment - coming soon)

## Setup
1. Clone the repo
2. Create a virtual environment and activate it
3. Run `pip install -r requirements.txt`
4. Create a `.env` file with your `GEMINI_API_KEY`
5. Run `streamlit run app.py`

## Project Structure
```
social-evaluator/
├── prompts/
│   ├── linkedin.txt
│   ├── instagram.txt
│   └── substack.txt
├── app.py
├── evaluate.py
├── requirements.txt
└── .env (not committed)
```
