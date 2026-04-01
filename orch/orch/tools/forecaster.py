import pandas as pd
import numpy as np
from typing import Optional, List, Union
from pathlib import Path

def forecast_series(file_path: str, column: str, periods: int = 5) -> str:
    """
    Predicts future values for a given column in a CSV or Excel file 
    using a simple linear trend model.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' not found."

        if path.suffix == '.csv':
            df = pd.read_csv(file_path)
        elif path.suffix in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path)
        else:
            return f"Error: Unsupported file format '{path.suffix}'."

        if column not in df.columns:
            return f"Error: Column '{column}' not found in the dataset. Available: {list(df.columns)}"

        # Prepare the data (assuming numeric)
        data = pd.to_numeric(df[column], errors='coerce').dropna()
        if len(data) < 2:
            return f"Error: Not enough numeric data in column '{column}' to perform a forecast."

        # Simple Linear Regression (Trend)
        y = data.values
        x = np.arange(len(y))
        
        # Calculate slope (m) and intercept (b)
        m, b = np.polyfit(x, y, 1)
        
        # Generate future indices
        future_x = np.arange(len(y), len(y) + periods)
        future_y = m * future_x + b
        
        # Round the results for readability
        future_y = [round(val, 2) for val in future_y]
        
        report = f"### Forecast Report for '{column}'\n\n"
        report += f"- **Method:** Simple Linear Trend\n"
        report += f"- **Detected Trend:** {'Upward' if m > 0 else 'Downward' if m < 0 else 'Stable'} (slope: {m:.4f})\n"
        report += f"- **Forecasted next {periods} periods:**\n\n"
        
        for i, val in enumerate(future_y, 1):
            report += f"  - Period {i}: **{val}**\n"
            
        return report

    except Exception as e:
        return f"Error during forecasting: {str(e)}"
