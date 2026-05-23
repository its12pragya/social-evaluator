import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PLATFORMS = ["linkedin", "instagram", "substack"]

def load_prompt(platform: str, post: str) -> str:
    prompt_path = f"prompts/{platform}.txt"
    with open(prompt_path, "r") as f:
        template = f.read()
    return template.replace("{post}", post)

def evaluate_post(platform: str, post: str) -> dict:
    prompt = load_prompt(platform, post)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    raw = response.text.strip()

    # Strip markdown code fences if model adds them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())

def print_results(result: dict):
    print(f"\n{'='*50}")
    print(f"Platform: {result['platform'].upper()}")
    print(f"Overall Score: {result['overall_score']}/10")
    print(f"{'='*50}")

    print("\nDIMENSION SCORES:")
    for d in result["dimensions"]:
        print(f"\n{d['name']}: {d['score']}/10")
        print(f"  Reasoning : {d['reasoning']}")
        print(f"  Suggestion: {d['suggestion']}")

    print("\nTOP IMPROVEMENTS:")
    for i, tip in enumerate(result["top_improvements"], 1):
        print(f"  {i}. {tip}")

    print(f"\nREWRITE SUGGESTION:\n  {result['rewrite_suggestion']}")

def main():
    print("Social Media Post Evaluator")
    print("----------------------------")

    print(f"Platforms: {', '.join(PLATFORMS)}")
    platform = input("Choose platform: ").strip().lower()

    if platform not in PLATFORMS:
        print(f"Invalid platform. Choose from: {', '.join(PLATFORMS)}")
        return

    print("Paste your post below. Press Enter twice when done:")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    post = "\n".join(lines)

    if not post.strip():
        print("No post provided.")
        return

    print("\nEvaluating...")
    result = evaluate_post(platform, post, context, post_goal)
    print_results(result)

if __name__ == "__main__":
    main()