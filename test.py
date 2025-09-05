from google import genai
import json

client = genai.Client()

myFile = client.files.get(name="files/jkrq5wwpit2h")

prompt = """
You are an expert public speaking coach.
I will give you an audio file of someone speaking.
Your task is to analyze the speech and return actionable feedback.

Focus on:
- Clarity
- Pronunciation
- Pacing
- Pauses
- Filler words
- Overall delivery

Rules:
- Output must be valid JSON only.
- No explanations outside the JSON.
- Each feedback item must have: "category", "issue", and "suggestion".

Example format:
{
  "feedback": [
    {
      "category": "Pauses",
      "issue": "The speaker rushed through ideas without pausing.",
      "suggestion": "Take a short pause between sentences."
    },
    {
      "category": "Filler Words",
      "issue": "Too many 'um' and 'uh'.",
      "suggestion": "Practice removing filler words."
    }
  ]
}
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[prompt, myFile]
)
print(json.loads( response.text.replace("```json", "").replace("```", "")))