from orch.orch.tool_runtime import execute_tool_code


def test_execute_tool_code_rejects_unknown_tool():
    result = execute_tool_code('does_not_exist("x")')
    assert "Tool 'does_not_exist' not found" in result


def test_execute_tool_code_rejects_non_literal_arguments():
    result = execute_tool_code("read_file(path_var)")
    assert "Only literal arguments are supported." in result
