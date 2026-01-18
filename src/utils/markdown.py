import pandas as pd


def h1(title: str) -> str:
    return f"# {title}\n"


def h2(title: str) -> str:
    return f"## {title}\n"


def h3(title: str) -> str:
    return f"### {title}\n"


def paragraph(text: str) -> str:
    return f"{text}\n"


def bullet_item(text: str) -> str:
    return f"- {text}\n"


def code_block(code: str, language: str = "") -> str:
    return f"```{language}\n{code}\n```\n"


def horizontal_rule() -> str:
    return "\n---\n"


def link(text: str, url: str) -> str:
    return f"[{text}]({url})"


def table(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False) + "\n"


class MarkdownBuilder:
    def __init__(self):
        self.contents = []

    def add(self, markdown: str):
        self.contents.append(markdown)

    def to_string(self) -> str:
        return "\n".join(self.contents)
