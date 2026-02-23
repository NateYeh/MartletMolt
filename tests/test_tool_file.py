import os
import pytest
from martlet_molt.tools.file_read import FileReadTool
from martlet_molt.tools.file_write import FileWriteTool

@pytest.fixture
def temp_file(tmp_path):
    f = tmp_path / "test.txt"
    content = "line1\nline2\nline3\nline4\nline5"
    f.write_text(content, encoding="utf-8")
    return f

def test_file_read_basic(temp_file):
    tool = FileReadTool()
    result = tool.execute(file_path=str(temp_file))
    
    assert result.success is True
    assert "line1" in result.data["content"]
    assert "line5" in result.data["content"]
    assert result.data["total_lines"] == 5

def test_file_read_range(temp_file):
    tool = FileReadTool()
    result = tool.execute(file_path=str(temp_file), start_line=2, end_line=3, show_line_numbers=False)
    
    assert result.success is True
    assert result.data["content"] == "line2\nline3"
    assert result.data["read_lines"] == 2

def test_file_read_not_found():
    tool = FileReadTool()
    result = tool.execute(file_path="/tmp/non_existent_file_12345.txt")
    assert result.success is False
    assert "File not found" in result.error

def test_file_write_new(tmp_path):
    f_path = tmp_path / "new_file.txt"
    tool = FileWriteTool()
    result = tool.execute(file_path=str(f_path), content="hello world")
    
    assert result.success is True
    assert f_path.exists()
    assert f_path.read_text() == "hello world"

def test_file_write_append(temp_file):
    tool = FileWriteTool()
    result = tool.execute(file_path=str(temp_file), content="\nline6", mode="append")
    
    assert result.success is True
    content = temp_file.read_text()
    assert "line6" in content
    assert content.endswith("line6")

def test_file_write_backup(temp_file):
    tool = FileWriteTool()
    # 建立備份
    result = tool.execute(file_path=str(temp_file), content="new content", backup=True)
    
    assert result.success is True
    bak_path = temp_file.with_suffix(".txt.bak")
    assert bak_path.exists()
    assert "line1" in bak_path.read_text()
    assert temp_file.read_text() == "new content"
