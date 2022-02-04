import re


def slug_transformer(text: str) -> str:
    text_lowercase = text.lower()
    text_split = re.split('[ :;?#/@%<>"{}&*=()$]', text_lowercase)
    if len(text_split) == 1:
        return text_lowercase
    else:
        return "-".join(text_split)
