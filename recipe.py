from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import google.generativeai as genai

app = Flask(__name__)

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

cuisines = [
    "",
    "Italian",
    "Mexican",
    "Chinese",
    "Indian",
    "Japanese",
    "Thai",
    "French",
    "Mediterranean",
    "American",
    "Greek",
    "Korean"
]

dietary_restrictions = [
    "Gluten-Free",
    "Dairy-Free",
    "Vegan",
    "Pescatarian",
    "Nut-Free",
    "Kosher",
    "Halal",
    "Low-Carb",
    "Organic",
    "Locally Sourced"
]

languages = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Russian": "ru",
    "Chinese (Simplified)": "zh-CN",
    "Chinese (Traditional)": "zh-TW",
    "Japanese": "ja",
    "Korean": "ko",
    "Italian": "it",
    "Portuguese": "pt",
    "Arabic": "ar",
    "Dutch": "nl",
    "Swedish": "sv",
    "Turkish": "tr",
    "Greek": "el",
    "Hebrew": "he",
    "Hindi": "hi",
    "Indonesian": "id",
    "Thai": "th",
    "Filipino": "tl",
    "Vietnamese": "vi"
}


def clean_gemini_response(text):
    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```", "", 1).strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    return text


@app.route("/")
def index():
    return render_template(
        "index.html",
        cuisines=cuisines,
        dietary_restrictions=dietary_restrictions,
        languages=languages
    )


@app.route("/generate_recipe", methods=["POST"])
def generate_recipe():
    ingredients = request.form.getlist("ingredient")
    selected_cuisine = request.form.get("cuisine")
    selected_restrictions = request.form.getlist("restrictions")
    selected_language = request.form.get("language")

    if len(ingredients) != 3:
        return "Kindly provide exactly 3 ingredients."

    prompt = f"""
    Create a recipe using only these three main ingredients: {', '.join(ingredients)}.

    Output rules:
    - Write the answer as an HTML fragment only.
    - Do not include ```html.
    - Do not include ``` code fences.
    - Do not include markdown formatting.
    - Do not explain that this is HTML.
    - Start directly with an HTML heading tag.
    - Put the ingredients section first.
    - Put the step-by-step cooking instructions after the ingredients.
    """

    if selected_cuisine:
        prompt += f"\nThe cuisine should be {selected_cuisine}."

    if selected_restrictions and len(selected_restrictions) > 0:
        prompt += f"\nThe recipe should have the following restrictions: {', '.join(selected_restrictions)}."

    if selected_language:
        prompt += f"\nWrite the entire recipe in {selected_language}."

    try:
        response = model.generate_content(prompt)
        recipe = clean_gemini_response(response.text)
    except Exception as e:
        recipe = f"Error generating recipe: {str(e)}"

    return render_template("recipe.html", recipe=recipe)


if __name__ == "__main__":
    app.run(debug=True)