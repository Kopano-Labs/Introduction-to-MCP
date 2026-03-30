from pydantic import Field
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

@mcp.resource("resource://doc_ids", name="doc_ids", description="Returns a list of all available document IDs.")
def list_doc_ids():
    """Returns a list of all document IDs."""
    return list(docs.keys())

@mcp.resource("resource://docs/{doc_id}", name="document_content", description="Returns the content of a specific document.")
def get_doc_content(doc_id: str):
    """Returns the content for a given doc_id."""
    if doc_id not in docs:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    return docs[doc_id]

@mcp.prompt(name="rewrite_as_markdown", description="Rewrite a document in markdown format.")
def rewrite_as_markdown(doc_id: str):
    """Generates a prompt to rewrite a document as markdown."""
    if doc_id not in docs:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    content = docs[doc_id]
    return [{"role": "user", "content": f"Please rewrite the following document content into well-formatted markdown:\n\n---\n\n{content}"}]

@mcp.prompt(name="summarize_doc", description="Summarize the contents of a document.")
def summarize_doc(doc_id: str):
    """Generates a prompt to summarize a document."""
    if doc_id not in docs:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    content = docs[doc_id]
    return [{"role": "user", "content": f"Please provide a concise summary of the following document:\n\n---\n\n{content}"}]

@mcp.tool (
    name="edit_documents",
    description="Edit a doucument by replacing a sting in the document content with a new string",
)
def edit_document(
    doc_id: str = Field(description="Id of the document that will be edited"),
    old_str: str = Field(description="The text to replace. Must match exactly, including whitespace"),
    new_str: str = Field(description="The new text to insert in the old text")
):
    if doc_id not in docs:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return docs[doc_id]

@mcp.tool (
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string",
)
def read_document(
    doc_id: str = Field(description="Id of the document to read"),
):
    if doc_id not in docs:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    return docs[doc_id]

if __name__ == "__main__":
    mcp.run(transport="stdio")
