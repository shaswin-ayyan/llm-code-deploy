import base64
import csv
import io
from typing import List, Dict

def generate_app(brief: str, attachments: List[Dict[str, str]]):
    """
    A mock LLM-assisted application generator.

    For now, it's hardcoded to handle the "sum-of-sales" task.
    """
    print("Starting application generation...")

    # Find the data.csv attachment
    csv_attachment = next((att for att in attachments if att['name'] == 'data.csv'), None)
    if not csv_attachment:
        raise ValueError("Required 'data.csv' attachment not found.")

    # Decode the base64 content
    try:
        # The URL is a data URI: data:text/csv;base64,.....
        header, encoded = csv_attachment['url'].split(',', 1)
        decoded_csv = base64.b64decode(encoded).decode('utf-8')
    except (ValueError, TypeError) as e:
        raise ValueError(f"Failed to decode base64 content from attachment: {e}")

    # Process the CSV and sum the 'sales' column
    total_sales = 0
    try:
        csv_reader = csv.DictReader(io.StringIO(decoded_csv))
        for row in csv_reader:
            total_sales += float(row.get('sales', 0))
    except (csv.Error, ValueError) as e:
        raise ValueError(f"Error processing CSV data: {e}")

    # Generate the HTML content
    # Brief: "Publish a single-page site that fetches data.csv from attachments,
    # sums its sales column, sets the title to "Sales Summary ${seed}",
    # displays the total inside #total-sales, and loads Bootstrap 5 from jsdelivr."

    # Extract seed from brief for the title (mocking this part)
    seed = "mock_seed" # In a real scenario, this would be parsed more robustly
    title = f"Sales Summary {seed}"

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>Sales Summary</h1>
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Total Sales</h5>
                <p class="card-text fs-4" id="total-sales">{total_sales:.2f}</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

    print("Application generation complete.")
    # Return the generated files
    return {"index.html": html_content}
