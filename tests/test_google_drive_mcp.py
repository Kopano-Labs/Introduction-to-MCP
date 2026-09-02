"""
Unit tests for Google Drive MCP Tool & Cognition Indexer
=======================================================
Verifies:
- SQLite Datalake initialization and caching
- Full-text and keyword search across Drive documents
- Document reading and export
- MCP Tool schema registration

I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

import pytest
from pathlib import Path
from kopano.tools.google_drive_mcp import GoogleDriveMCPTool, DriveDocument


@pytest.fixture
def drive_tool(tmp_path, monkeypatch):
    test_db = tmp_path / "test_gdrive_cache.db"
    monkeypatch.setenv("DRIVE_CACHE_DB", str(test_db))
    tool = GoogleDriveMCPTool()
    return tool


def test_cache_and_search_document(drive_tool):
    doc1 = DriveDocument(
        file_id="gdoc_001",
        name="GSMB 2026 Sovereign Architecture Blueprint",
        mime_type="application/vnd.google-apps.document",
        content_text="The 10-Seat Round Table Council governs all multi-agent orchestration and local execution on the Black Beast.",
        web_view_link="https://docs.google.com/document/d/gdoc_001/edit"
    )
    doc2 = DriveDocument(
        file_id="gdoc_002",
        name="Township AI Apprenticeship Curriculum 2026",
        mime_type="application/vnd.google-apps.document",
        content_text="Cassey Seat 2 leads the STP pedagogy for township interns across South Africa.",
        web_view_link="https://docs.google.com/document/d/gdoc_002/edit"
    )
    drive_tool.cache_document(doc1)
    drive_tool.cache_document(doc2)

    # Search by keyword
    results1 = drive_tool.search_drive("Black Beast")
    assert len(results1) == 1
    assert results1[0]["file_id"] == "gdoc_001"
    assert "10-Seat" in results1[0]["preview"]

    # Search by title keyword
    results2 = drive_tool.search_drive("Township")
    assert len(results2) == 1
    assert results2[0]["file_id"] == "gdoc_002"


def test_read_document(drive_tool):
    doc = DriveDocument(
        file_id="gdoc_003",
        name="KPCB Plus Protocol Laws",
        mime_type="application/vnd.google-apps.document",
        content_text="[EP] Execution Protocol + [BP] Boundary Protocol * [PP] Pedagogical Protocol."
    )
    drive_tool.cache_document(doc)

    retrieved = drive_tool.read_document("gdoc_003")
    assert retrieved is not None
    assert retrieved.name == "KPCB Plus Protocol Laws"
    assert "Execution Protocol" in retrieved.content_text

    # Non-existent doc
    assert drive_tool.read_document("non_existent_id") is None


def test_mcp_tool_definitions(drive_tool):
    defs = drive_tool.get_tool_definitions()
    assert len(defs) == 3
    tool_names = [d["name"] for d in defs]
    assert "google_drive_search" in tool_names
    assert "google_drive_read_doc" in tool_names
    assert "google_drive_list_recent" in tool_names
