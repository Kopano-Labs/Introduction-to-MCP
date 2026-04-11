import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import os
from typing import Dict, Union

def generate_plot(data: Dict[str, Union[int, float]], title: str = "Data Visualization", plot_type: str = "bar", output_path: str = "plot.png") -> str:
    """
    Generates a simple data visualization (bar chart, line chart, or pie chart) and saves it to a file.
    
    Parameters:
    - data: A dictionary where keys are labels and values are numeric data points.
    - title: The title of the plot.
    - plot_type: The type of plot to generate ('bar', 'line', or 'pie').
    - output_path: The path where the generated plot image should be saved.
    
    Returns:
    - A success or error message.
    """
    if not isinstance(data, dict):
        return "Error: Data must be a dictionary of labels and numeric values."
    
    try:
        labels = list(data.keys())
        values = list(data.values())
        
        plt.figure(figsize=(10, 6))
        
        if plot_type == "bar":
            plt.bar(labels, values, color='skyblue')
        elif plot_type == "line":
            plt.plot(labels, values, marker='o', linestyle='-', color='orange')
        elif plot_type == "pie":
            plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
        else:
            plt.close()
            return f"Error: Unsupported plot type '{plot_type}'. Use 'bar', 'line', or 'pie'."
        
        plt.title(title)
        plt.xlabel("Categories")
        plt.ylabel("Values")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plt.savefig(output_path)
        plt.close()
        
        return f"Plot '{title}' successfully generated and saved to: {output_path}"
    except Exception as e:
        plt.close()
        return f"Error generating plot: {e}"
