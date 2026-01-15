"""Excel file generation and conditional formatting."""

from openpyxl import load_workbook
from openpyxl.formatting.rule import ColorScaleRule, Rule
from openpyxl.styles import PatternFill
from openpyxl.styles.differential import DifferentialStyle
from reporting.formatters import optimize_column_widths


def apply_conditional_formatting(xlsx_path, num_rows):
    """
    Apply conditional formatting and optimize column widths for Excel file.

    Color Scheme:
    - Z-scores: Red (extreme ±2) → White (neutral 0) → Yellow (moderate)
    - Returns/TSMOM: Red (negative) → White (0) → Green (positive)
    - ADX/Scores: White (low) → Green (high)
    - VIX: Green (low) → Red (high) - inverted scale

    Args:
        xlsx_path: Path to the Excel file
        num_rows: Number of data rows (excluding header) - used for dynamic range formatting
    """
    wb = load_workbook(xlsx_path)

    # === WEEKLY SHEET ===
    if 'Weekly' in wb.sheetnames:
        ws = wb['Weekly']

        # Z-Score: -2 (red) → 0 (white) → +2 (yellow/orange)
        ws.conditional_formatting.add(f'D2:D{num_rows+1}',
            ColorScaleRule(start_type='num', start_value=-2, start_color='F8696B',  # Red
                          mid_type='num', mid_value=0, mid_color='FFFFFF',          # White
                          end_type='num', end_value=2, end_color='FFEB84'))         # Yellow

        # TSMOM_%: -20 (red) → 0 (white) → +20 (green)
        ws.conditional_formatting.add(f'E2:E{num_rows+1}',
            ColorScaleRule(start_type='num', start_value=-20, start_color='F8696B',  # Red
                          mid_type='num', mid_value=0, mid_color='FFFFFF',           # White
                          end_type='num', end_value=20, end_color='63BE7B'))         # Green

        # MA_Score: 0 (white) → 7 (green)
        ws.conditional_formatting.add(f'F2:F{num_rows+1}',
            ColorScaleRule(start_type='num', start_value=0, start_color='FFFFFF',   # White
                          end_type='num', end_value=7, end_color='63BE7B'))          # Green

        # ADX: 10 (white) → 50 (green)
        ws.conditional_formatting.add(f'H2:H{num_rows+1}',
            ColorScaleRule(start_type='num', start_value=10, start_color='FFFFFF',  # White
                          end_type='num', end_value=50, end_color='63BE7B'))         # Green

        # Optimize column widths
        optimize_column_widths(ws)

    # === MOMENTUM SHEET ===
    if 'Momentum' in wb.sheetnames:
        ws = wb['Momentum']

        # All return columns: -30 (red) → 0 (white) → +30 (green)
        for col in ['C', 'D', 'E']:  # 4w, 12w, 26w returns
            ws.conditional_formatting.add(f'{col}2:{col}{num_rows+1}',
                ColorScaleRule(start_type='num', start_value=-30, start_color='F8696B',  # Red
                              mid_type='num', mid_value=0, mid_color='FFFFFF',           # White
                              end_type='num', end_value=30, end_color='63BE7B'))         # Green

        # Optimize column widths
        optimize_column_widths(ws)

    # === DAILY SHEET ===
    if 'Daily' in wb.sheetnames:
        ws = wb['Daily']

        # Z-Score: -2 (red) → 0 (white) → +2 (yellow)
        ws.conditional_formatting.add(f'D2:D{num_rows+1}',
            ColorScaleRule(start_type='num', start_value=-2, start_color='F8696B',
                          mid_type='num', mid_value=0, mid_color='FFFFFF',
                          end_type='num', end_value=2, end_color='FFEB84'))

        # ADX: 10 (white) → 50 (green)
        ws.conditional_formatting.add(f'G2:G{num_rows+1}',
            ColorScaleRule(start_type='num', start_value=10, start_color='FFFFFF',
                          end_type='num', end_value=50, end_color='63BE7B'))

        # Crosses: Highlight Bullish in green, Bearish in red
        green_fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
        red_fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')

        # Use formula-based rules for text contains
        ws.conditional_formatting.add(f'F2:F{num_rows+1}',
            Rule(type='containsText', operator='containsText', formula=['SEARCH("Bullish",F2)'],
                 dxf=DifferentialStyle(fill=green_fill), text='Bullish'))
        ws.conditional_formatting.add(f'F2:F{num_rows+1}',
            Rule(type='containsText', operator='containsText', formula=['SEARCH("Bearish",F2)'],
                 dxf=DifferentialStyle(fill=red_fill), text='Bearish'))

        # Consensus: -1 (red) → 0 (white) → +1 (green)
        ws.conditional_formatting.add(f'H2:H{num_rows+1}',
            ColorScaleRule(start_type='num', start_value=-1, start_color='F8696B',
                          mid_type='num', mid_value=0, mid_color='FFFFFF',
                          end_type='num', end_value=1, end_color='63BE7B'))

        # Confidence: 0 (white) → 1 (green)
        ws.conditional_formatting.add(f'I2:I{num_rows+1}',
            ColorScaleRule(start_type='num', start_value=0, start_color='FFFFFF',
                          end_type='num', end_value=1, end_color='63BE7B'))

        # Optimize column widths
        optimize_column_widths(ws)

    # === MACRO SHEET ===
    if 'Macro' in wb.sheetnames:
        ws = wb['Macro']

        # VIX (row with VIX indicator): 10 (green/calm) → 40 (red/fear) - INVERTED
        # Find the row with VIX indicator
        for row_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=10, min_col=1, max_col=1), start=1):
            if row[0].value == 'VIX':
                ws.conditional_formatting.add(f'B{row_idx}:B{row_idx}',
                    ColorScaleRule(start_type='num', start_value=10, start_color='63BE7B',  # Green
                                  end_type='num', end_value=40, end_color='F8696B'))        # Red
                break

        # -Z(VIX): -2 (red/fear) → 0 (white) → +2 (orange/complacency)
        for row_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=10, min_col=1, max_col=1), start=1):
            if row[0].value == '-Z(VIX)':
                ws.conditional_formatting.add(f'B{row_idx}:B{row_idx}',
                    ColorScaleRule(start_type='num', start_value=-2, start_color='F8696B',
                                  mid_type='num', mid_value=0, mid_color='FFFFFF',
                                  end_type='num', end_value=2, end_color='FFEB84'))
                break

        # F&G indices: 0 (red/fear) → 50 (white) → 100 (red/greed)
        for row_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=15, min_col=1, max_col=1), start=1):
            if row[0].value in ['F&G Stocks', 'F&G Crypto']:
                ws.conditional_formatting.add(f'B{row_idx}:B{row_idx}',
                    ColorScaleRule(start_type='num', start_value=0, start_color='F8696B',
                                  mid_type='num', mid_value=50, mid_color='FFFFFF',
                                  end_type='num', end_value=100, end_color='F8696B'))

        # Optimize column widths
        optimize_column_widths(ws)

    wb.save(xlsx_path)
    print(f"  - Applied conditional formatting and optimized column widths")
