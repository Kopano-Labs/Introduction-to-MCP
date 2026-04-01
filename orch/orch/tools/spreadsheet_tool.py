import pandas as pd
import os
from pathlib import Path

def clean_spreadsheet(file_path: str, output_path: str = None) -> str:
    """
    Cleans a CSV or Excel spreadsheet by removing duplicates, handling missing values, 
    and standardizing text casing.
    
    Parameters:
    - file_path: Path to the CSV or Excel file to clean.
    - output_path: Optional path to save the cleaned file. If not provided, appends '_cleaned' to the filename.
    
    Returns:
    - A success or error message.
    """
    path = Path(file_path)
    if not path.exists():
        return f"Error: File not found at {file_path}"
    
    try:
        # Determine file type and read
        if path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        elif path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            return f"Error: Unsupported file format {path.suffix}. Use CSV or Excel."
        
        # 1. Remove duplicates
        initial_count = len(df)
        df.drop_duplicates(inplace=True)
        dropped_duplicates = initial_count - len(df)
        
        # 2. Standardize text casing and strip whitespace for string columns
        for col in df.select_dtypes(include=['object']):
            df[col] = df[col].astype(str).str.strip().str.title()
            # Handle 'Nan' strings that might have been created from actual NaN values
            df[col] = df[col].replace('Nan', None)
        
        # 3. Handle missing values (e.g., fill with 'Unknown' or 0 depending on type)
        # For simplicity, we'll leave them as is unless specified, but let's drop rows with all NaN
        df.dropna(how='all', inplace=True)
        
        # Define output path
        if not output_path:
            output_path = f"{path.stem}_cleaned{path.suffix}"
        
        # Save the result
        if path.suffix.lower() == '.csv':
            df.to_csv(output_path, index=False)
        else:
            df.to_excel(output_path, index=False)
            
        return f"Spreadsheet cleaned successfully! Dropped {dropped_duplicates} duplicates. Saved to: {output_path}"
    except Exception as e:
        return f"Error cleaning spreadsheet: {e}"
