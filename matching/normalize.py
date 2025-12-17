import re
import unicodedata

def normalize(text):
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[\(\[].*?[\)\]]", "", text)
    text = re.sub(r"\b(feat|ft)\b.*", "", text)
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()
