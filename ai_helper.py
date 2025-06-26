# ai_helper.py  – REVISION
import os, openai, textwrap
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

_SYSTEM = """
You are a friendly RF-systems tutor.  Turn the raw data you receive
into a short *story-style* explanation that walks step-by-step 
Keep the whole answer under 140 words.
"""

def explain(topic: str, inputs: dict, outputs: dict) -> str:
    data = "INPUTS\n"  + "\n".join(f"{k}: {v}" for k,v in inputs.items())
    data+= "\nOUTPUTS\n"+ "\n".join(f"{k}: {v}" for k,v in outputs.items())

    rsp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system", "content":_SYSTEM},
            {"role":"user",   "content":f"Topic={topic}\n{data}"}
        ],
        max_tokens=180,
        temperature=0.4,
    )
    return textwrap.fill(rsp.choices[0].message.content, 90)
