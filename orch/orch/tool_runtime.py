import ast
import importlib


TOOL_FUNCTIONS_MAP = {
    "search": ("search", "perform_search"),
    "read_file": ("filesystem", "read_file"),
    "write_file": ("filesystem", "write_file"),
    "list_directory": ("filesystem", "list_directory"),
    "delete_file": ("filesystem", "delete_file"),
    "execute_code": ("code_execution", "execute_code"),
    "git_init": ("git", "git_init"),
    "git_add": ("git", "git_add"),
    "git_commit": ("git", "git_commit"),
    "git_status": ("git", "git_status"),
    "git_log": ("git", "git_log"),
    "scan_code_security": ("security", "scan_code_security"),
    "scan_dependencies": ("security", "scan_dependencies"),
    "monitor_brand": ("social_monitor", "monitor_brand"),
    "generate_report": ("report_generator", "generate_report"),
    "search_arxiv": ("arxiv", "search_arxiv"),
    "scrape_page": ("web_scraper", "scrape_page"),
    "sql_query": ("database_tool", "sql_query"),
    "clean_spreadsheet": ("spreadsheet_tool", "clean_spreadsheet"),
    "generate_plot": ("viz_tool", "generate_plot"),
    "analyze_logs": ("log_analyzer", "analyze_logs"),
    "compare_datasets": ("data_comparator", "compare_datasets"),
    "analyze_sentiment": ("sentiment_analyzer", "analyze_sentiment"),
    "detect_anomalies": ("anomaly_detector", "detect_anomalies"),
    "ab_test_analysis": ("ab_tester", "ab_test_analysis"),
    "forecast_series": ("forecaster", "forecast_series"),
    "get_loadshedding_status": ("loadshedding", "get_loadshedding_status"),
    "is_gig_safe": ("loadshedding", "is_gig_safe"),
    "match_gig": ("gig_matcher", "match_gig"),
    "rank_providers": ("gig_matcher", "rank_providers"),
}


def get_tools_prompt() -> str:
    """Generates the tool usage instructions for the agent's system prompt."""
    return """
You have access to the following tools. To use a tool, respond with ONLY the tool call inside <tool_code> XML tags.
Example: <tool_code>write_file("path/to/file.txt", "File content here.")</tool_code>

Available Tools:
- read_file(file_path: str): Reads the content of a specified file.
- write_file(file_path: str, content: str): Writes content to a specified file, creating directories if they don't exist.
- list_directory(directory_path: str = "."): Lists the contents of a directory.
- delete_file(file_path: str): Deletes a file.
- search(query: str, search_depth: str = "basic"): Performs a web search for a given query. Use search_depth='advanced' for more comprehensive results.
- execute_code(code: str): Executes Python code and returns the result.
- git_init(): Initializes a new Git repository.
- git_add(file_path: str): Adds a file to the Git staging area.
- git_commit(message: str): Commits staged changes with a message.
- git_status(): Shows the Git repository status.
- git_log(): Shows the Git commit log.
- scan_code_security(target_path: str): Scans Python code for security issues using Bandit.
- scan_dependencies(requirements_file: str = "requirements.txt"): Scans project dependencies for known vulnerabilities using Safety.
- monitor_brand(brand_name: str, platform: str = "all"): Monitors social media (Reddit, X, etc.) for brand mentions.
- generate_report(title: str, sections: dict, file_name: str = "report.md"): Generates a structured Markdown report or deck.
- search_arxiv(query: str): Searches arXiv for the latest papers on a given topic.
- scrape_page(url: str, selector: str = "body"): Scrapes the text content of a web page.
- sql_query(query: str): Executes a SQL query against the Data Lake SQLite database.
- clean_spreadsheet(file_path: str, output_path: str = None): Cleans a CSV or Excel spreadsheet by removing duplicates, handling missing values, and standardizing text casing.
- generate_plot(data: dict, title: str = "Data Visualization", plot_type: str = "bar", output_path: str = "plot.png"): Generates and saves a data visualization image.
- analyze_logs(file_path: str): Analyzes a log file and returns a structured Markdown summary.
- compare_datasets(file1: str, file2: str): Compares two datasets (JSON, JSONL, or CSV) and highlights differences.
- analyze_sentiment(text: str): Analyzes the sentiment of a given text (positive, negative, or neutral).
- detect_anomalies(): Analyzes the Data Lake for performance anomalies, security alerts, and execution corrections.
- ab_test_analysis(): Performs A/B testing analysis on agents/models based on historical performance metrics in the Data Lake.
- forecast_series(file_path: str, column: str, periods: int = 5): Predicts future values for a given column in a CSV or Excel file using a simple linear trend model.
- get_loadshedding_status(area_id: str): Returns a simplified loadshedding snapshot for an area.
- is_gig_safe(area_id: str, start_time: str, duration_hours: float = 1.0): Checks whether a gig overlaps with loadshedding.
- match_gig(description: str, location: str, category: str, skills: list, providers: list): Ranks providers for a gig.
- rank_providers(providers: list, criteria: dict): Ranks providers against scoring criteria.
"""


def execute_tool_code(tool_code: str) -> str:
    """Executes a tool call string like 'read_file(\"file.txt\")'."""
    try:
        tree = ast.parse(tool_code.strip())

        if not isinstance(tree, ast.Module) or len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr) or not isinstance(tree.body[0].value, ast.Call):
            return f"Error: '{tool_code}' is not a valid single tool call."

        call_node = tree.body[0].value
        if not isinstance(call_node.func, ast.Name):
            return "Error: Complex function calls are not supported."

        tool_name = call_node.func.id
        if tool_name not in TOOL_FUNCTIONS_MAP:
            return f"Error: Tool '{tool_name}' not found."

        args = []
        for arg in call_node.args:
            if isinstance(arg, ast.Constant):
                args.append(arg.value)
            else:
                return "Error: Only literal arguments are supported."

        kwargs = {}
        for kw in call_node.keywords:
            if isinstance(kw.value, ast.Constant):
                kwargs[kw.arg] = kw.value.value
            else:
                return "Error: Only literal keyword arguments are supported."

        module_name, function_name = TOOL_FUNCTIONS_MAP[tool_name]
        tool_module = importlib.import_module(f"orch.orch.tools.{module_name}")
        tool_function = getattr(tool_module, function_name)
        result = tool_function(*args, **kwargs)
        return str(result)
    except Exception as e:
        return f"Error executing tool code '{tool_code}': {e}"
