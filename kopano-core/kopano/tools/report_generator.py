from pathlib import Path
from typing import Dict, Union

def generate_report(title: str, sections: Dict[str, str], file_name: str = "report.md") -> str:
    """
    Generates a structured Markdown report or deck.
    
    Args:
        title: The title of the report.
        sections: A dictionary where keys are section titles and values are section content.
        file_name: The name of the file to save the report to (defaults to 'report.md').
    """
    if not title or not sections:
        return "Error: Title and sections are required."

    try:
        content = f"# {title}\n\n"
        for section_title, section_content in sections.items():
            content += f"## {section_title}\n\n{section_content}\n\n"
        
        path = Path(file_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Successfully generated report '{file_name}'."
    except Exception as e:
        return f"Error generating report: {e}"
