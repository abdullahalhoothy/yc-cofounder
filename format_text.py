#!/usr/bin/env python3
"""
Script to reformat text by adding line breaks after approximately 15 words
"""

def format_text_with_line_breaks(text, words_per_line=15):
    """
    Format text by adding line breaks after approximately the specified number of words,
    while preserving the structure of the document (keeping separators and headers intact)
    
    Args:
        text (str): Input text to format
        words_per_line (int): Target number of words per line
    
    Returns:
        str: Formatted text with line breaks
    """
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Skip empty lines and separator lines
        if not line.strip() or line.strip().startswith('===='):
            formatted_lines.append(line)
            continue
            
        # Check if this is a header line (Date:, Name:, URL:, Reason:)
        if any(line.startswith(header) for header in ['Date:', 'Name:', 'URL:', 'Reason:']):
            # Split the content after the header
            if ':' in line:
                header_part, content_part = line.split(':', 1)
                content_part = content_part.strip()
                
                if content_part:
                    # Break up the content part into lines
                    words = content_part.split()
                    content_lines = []
                    current_line = []
                    
                    for word in words:
                        current_line.append(word)
                        if len(current_line) >= words_per_line:
                            content_lines.append(' '.join(current_line))
                            current_line = []
                    
                    # Add any remaining words
                    if current_line:
                        content_lines.append(' '.join(current_line))
                    
                    # Add the header with the first line of content
                    if content_lines:
                        formatted_lines.append(f"{header_part}: {content_lines[0]}")
                        # Add remaining content lines with proper indentation
                        for content_line in content_lines[1:]:
                            formatted_lines.append(content_line)
                    else:
                        formatted_lines.append(line)
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        else:
            # For non-header lines, break them up if they're too long
            words = line.split()
            if len(words) > words_per_line:
                current_line = []
                for word in words:
                    current_line.append(word)
                    if len(current_line) >= words_per_line:
                        formatted_lines.append(' '.join(current_line))
                        current_line = []
                
                if current_line:
                    formatted_lines.append(' '.join(current_line))
            else:
                formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def main():
    input_file = 'recommended_candidates.txt'
    output_file = 'formatted_candidates.txt'
    
    try:
        # Read the input file
        with open(input_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Format the content
        formatted_content = format_text_with_line_breaks(content, words_per_line=15)
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(formatted_content)
        
        print(f"Successfully formatted text from '{input_file}' and saved to '{output_file}'")
        print(f"Original file had {len(content.split())} words")
        print(f"Formatted into {len(formatted_content.split(chr(10)))} lines")
        
    except FileNotFoundError:
        print(f"Error: Could not find '{input_file}' in the current directory")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()