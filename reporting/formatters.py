"""Formatting utilities for Excel output."""


def format_sign(value):
    """Format number with + or - sign."""
    return f"{'+' if value >= 0 else ''}{value}"


def optimize_column_widths(ws):
    """Auto-adjust column widths based on content."""
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter

        for cell in column:
            try:
                if cell.value:
                    # Convert to string and measure length
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
            except:
                pass

        # Set width with some padding (add 2 for comfort)
        adjusted_width = min(max_length + 2, 50)  # Cap at 50 to avoid excessive width
        ws.column_dimensions[column_letter].width = adjusted_width
