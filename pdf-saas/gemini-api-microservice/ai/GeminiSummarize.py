import os
import json
import re
import google.genai as genai

class PDFSummarizer:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def _extract_json(self, text: str) -> str:
        """Extract and clean JSON from model output."""
        text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return match.group(0)
        return text

    def _fix_common_json_errors(self, text: str) -> str:
        """Try to fix common JSON formatting errors."""
        text = re.sub(r",\s*([\]}])", r"\1", text)  # remove trailing commas
        text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        text = re.sub(r",\s*,", ",", text)  # remove double commas
        return text

    def _json_safe_parse(self, text: str):
        """Try multiple ways to parse JSON safely."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            fixed = self._fix_common_json_errors(text)
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                # Last resort: insert missing commas between }{
                repaired = re.sub(r"}\s*{", "},{", fixed)
                repaired = re.sub(r'"\s*"', '", "', repaired)  # missing comma between strings
                try:
                    return json.loads(repaired)
                except json.JSONDecodeError as e:
                    return {
                        "error": "Failed to parse JSON after all cleanup attempts",
                        "fixed_output": repaired,
                        "json_error": str(e)
                    }

    def summarize_content(self, content: str, model: str = "gemini-2.5-flash") -> dict:
        """Summarize content, extract key points, and generate exactly 10 MCQs."""
        prompt = (
            "Analyze the following content and return ONLY valid JSON with three keys:\n"
            "1. 'summary' → a concise summary string.\n"
            "2. 'key_points' → a list of the most important points.\n"
            "3. 'mcq' → exactly 10 multiple-choice questions:\n"
            "   [{\"question\":\"\",\"option\":{\"a\":\"\",\"b\":\"\",\"c\":\"\",\"d\":\"\"},\"answer\":\"\",\"explanation\":\"\"}]\n"
            "Rules:\n"
            "- mcq must have exactly 10 questions.\n"
            "- answer must be one of 'a','b','c','d'.\n"
            "- explanation must justify the answer.\n"
            "- No markdown, no extra text, only JSON."
        )

        response = self.client.models.generate_content(
            model=model,
            contents=f"{prompt}\n\nContent:\n{content}"
        )

        raw_output = response.text.strip()
        cleaned_output = self._extract_json(raw_output)
        return self._json_safe_parse(cleaned_output)
