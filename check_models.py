from google import genai

c = genai.Client()
for m in ["models/gemini-4-argon", "models/gemini-4-neon", "models/gemini-3.5-flash-lite"]:
    try:
        res = c.models.generate_content(model=m, contents="say ok")
        print("WORKING:", m, "->", res.text.strip())
        break
    except Exception as e:
        print("SKIP:", m, "->", str(e)[:70])