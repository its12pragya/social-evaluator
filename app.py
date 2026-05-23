import os
import json
import streamlit as st
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PLATFORMS = ["linkedin", "instagram", "substack", "twitter"]

PLATFORM_TIPS = {
    "linkedin": "💼 Best for: Professional insights, personal stories, career lessons. Keep paragraphs short.",
    "instagram": "📸 Best for: Emotional hooks, personal vulnerability, relatable moments. First line is everything.",
    "substack": "📩 Best for: Long-form essays, strong thesis, distinct voice. Opening paragraph must create tension.",
    "twitter": "🐦 Best for: Sharp takes, punchy observations, conversation starters. Every word must earn its place."
}

CONTEXT_PLACEHOLDERS = {
    "linkedin": "e.g. Senior PM sharing lessons on product strategy, goal is to attract job opportunities",
    "instagram": "e.g. Travel blogger focused on solo female travel in Southeast Asia, goal is to grow followers",
    "substack": "e.g. Newsletter writer covering AI and creativity for non-technical readers, goal is to grow paid subscribers",
    "twitter": "e.g. Builder sharing lessons on indie hacking and AI tools, goal is to grow an audience of makers"
}

def load_prompt(platform: str, post: str, context: str, post_goal: str) -> str:
    prompt_path = f"prompts/{platform}.txt"
    with open(prompt_path, "r") as f:
        template = f.read()
    return (
        template
        .replace("{post}", post)
        .replace("{context}", context)
        .replace("{post_goal}", post_goal)
    )

def evaluate_post(platform: str, post: str, context: str = "", post_goal: str = "") -> dict:
    prompt = load_prompt(platform, post, context, post_goal)
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
    page_title="DraftLens",
    page_icon="🔍",
    layout="centered"
)

st.title("🔍 DraftLens")
st.caption("Paste your post, add context, get a detailed critique powered by Gemini 2.5 Flash.")

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

# --- Context inputs ---
st.subheader("2. Add your context")
col1, col2 = st.columns(2)

with col1:
    context = st.text_input(
        label="Who are you?",
        placeholder=CONTEXT_PLACEHOLDERS[platform],
        help="Your role, niche, or professional background"
    )

with col2:
    post_goal = st.text_input(
        label="What is this post about?",
        placeholder="e.g. Sharing a lesson I learned after a failed product launch",
        help="One line about what this specific post is trying to say or achieve"
    )

# --- Post input ---
st.subheader("3. Paste your post")

if platform == "twitter":
    post = st.text_area(
        label="Post content",
        placeholder="Paste your tweet here... (max 280 characters)",
        height=100,
        max_chars=280,
        label_visibility="collapsed"
    )
    char_count = len(post)
    st.caption(f"{char_count}/280 characters")
else:
    post = st.text_area(
        label="Post content",
        placeholder="Paste your LinkedIn post, Instagram caption, or Substack excerpt here...",
        height=200,
        label_visibility="collapsed"
    )

# --- Evaluate button ---
st.subheader("4. Evaluate")
if st.button("Evaluate Post ✦", use_container_width=True, type="primary"):
    if not post.strip():
        st.warning("Please paste a post before evaluating.")
    elif not context.strip():
        st.warning("Please add who you are before evaluating.")
    elif not post_goal.strip():
        st.warning("Please add what this post is about before evaluating.")
    else:
        with st.spinner("Gemini is reading your post..."):
            try:
                result = evaluate_post(platform, post, context, post_goal)

                # --- Overall score ---
                st.divider()
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.metric("Overall Score", f"{result['overall_score']}/10")
                with col2:
                    st.markdown(f"**Platform:** {result['platform'].capitalize()}")
                    st.markdown(f"**Who:** {context}")
                    st.markdown(f"**Post intent:** {post_goal}")
                    st.markdown(f"**Word count:** {len(post.split())} words")

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
                rewrite = result["rewrite_suggestion"]
                st.code(rewrite, language=None)

            except json.JSONDecodeError:
                st.error("Gemini returned an unexpected format. Try again.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")