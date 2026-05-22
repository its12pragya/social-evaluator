import os
import json
import streamlit as st
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PLATFORMS = ["linkedin", "instagram", "substack"]

PLATFORM_TIPS = {
    "linkedin": "💼 Best for: Professional insights, personal stories, career lessons. Keep paragraphs short.",
    "instagram": "📸 Best for: Emotional hooks, personal vulnerability, relatable moments. First line is everything.",
    "substack": "📩 Best for: Long-form essays, strong thesis, distinct voice. Opening paragraph must create tension."
}

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
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

def score_color(score: int) -> str:
    if score >= 8:
        return "🟢"
    elif score >= 5:
        return "🟡"
    else:
        return "🔴"

# --- Page config ---
st.set_page_config(
    page_title="Social Post Evaluator",
    page_icon="✍️",
    layout="centered"
)

st.title("✍️ Social Media Post Evaluator")
st.caption("Paste your post, pick a platform, get a detailed critique powered by Gemini 2.5 Flash.")

# --- Platform selector ---
st.subheader("1. Choose your platform")
platform = st.radio(
    label="Platform",
    options=PLATFORMS,
    format_func=lambda x: x.capitalize(),
    horizontal=True,
    label_visibility="collapsed"
)

st.info(PLATFORM_TIPS[platform])

# --- Post input ---
st.subheader("2. Paste your post")
post = st.text_area(
    label="Post content",
    placeholder="Paste your LinkedIn post, Instagram caption, or Substack excerpt here...",
    height=200,
    label_visibility="collapsed"
)

# --- Evaluate button ---
st.subheader("3. Evaluate")
if st.button("Evaluate Post ✦", use_container_width=True, type="primary"):
    if not post.strip():
        st.warning("Please paste a post before evaluating.")
    else:
        with st.spinner("Gemini is reading your post..."):
            try:
                result = evaluate_post(platform, post)

                # --- Overall score ---
                st.divider()
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.metric("Overall Score", f"{result['overall_score']}/10")
                with col2:
                    st.markdown(f"**Platform:** {result['platform'].capitalize()}")
                    st.markdown(f"**Post length:** {len(post.split())} words")

                # --- Dimension scores ---
                st.divider()
                st.subheader("Dimension Breakdown")
                for d in result["dimensions"]:
                    with st.expander(f"{score_color(d['score'])} {d['name']} — {d['score']}/10"):
                        st.markdown(f"**Reasoning:** {d['reasoning']}")
                        st.markdown(f"**Suggestion:** {d['suggestion']}")

                # --- Top improvements ---
                st.divider()
                st.subheader("Top Improvements")
                for i, tip in enumerate(result["top_improvements"], 1):
                    st.markdown(f"**{i}.** {tip}")

                # --- Rewrite suggestion ---
                st.divider()
                st.subheader("Rewrite Suggestion")
                st.markdown(result["rewrite_suggestion"])

            except json.JSONDecodeError:
                st.error("Gemini returned an unexpected format. Try again.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")