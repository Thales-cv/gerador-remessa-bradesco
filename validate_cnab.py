#!/usr/bin/env python3
"""
Validation script to check position 230 (Aviso ao Favorecido) in CNAB 240 files.
This script verifies that all Segmento A lines have '0' at position 230.
"""
import sys

def validate_cnab_file(filepath):
    """
    Validate CNAB 240 file for correct Aviso ao Favorecido field.
    
    Args:
        filepath: Path to the .REM file
        
    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []
    segmento_a_count = 0
    
    try:
        with open(filepath, 'r', encoding='cp1252') as f:
            for line_num, line in enumerate(f, 1):
                # Remove line endings but keep trailing spaces
                line = line.rstrip('\r\n')
                
                # Check if this is a Segmento A line
                # Format: Position 8 = '3' (detail record), Position 14 = 'A' (segment A)
                if len(line) >= 14 and line[7] == '3' and line[13] == 'A':
                    segmento_a_count += 1
                    
                    # Check line length
                    if len(line) != 240:
                        errors.append(f"Line {line_num}: Invalid length {len(line)}, expected 240")
                        continue
                    
                    # Check position 230 (index 229 in 0-based)
                    aviso_value = line[229]
                    if aviso_value != '0':
                        errors.append(
                            f"Line {line_num}: Position 230 = '{aviso_value}', expected '0' "
                            f"(Segmento A #{segmento_a_count})"
                        )
    
    except FileNotFoundError:
        errors.append(f"File not found: {filepath}")
    except Exception as e:
        errors.append(f"Error reading file: {str(e)}")
    
    return len(errors) == 0, errors, segmento_a_count

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_cnab.py <path_to_rem_file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    is_valid, errors, seg_a_count = validate_cnab_file(filepath)
    
    print(f"\\n{'='*60}")
    print(f"CNAB 240 Validation Results")
    print(f"{'='*60}")
    print(f"File: {filepath}")
    print(f"Segmento A lines found: {seg_a_count}")
    print(f"{'='*60}\\n")
    
    if is_valid:
        print("✅ VALIDATION PASSED!")
        print(f"All {seg_a_count} Segmento A lines have '0' at position 230.")
    else:
        print("❌ VALIDATION FAILED!")
        print(f"\\nErrors found ({len(errors)}):\\n")
        for error in errors:
            print(f"  • {error}")
        sys.exit(1)
