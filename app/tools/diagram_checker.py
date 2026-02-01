# def check_diagram(document: dict) -> dict:
#     """
#     Check for diagrams, figures, or images in document.
    
#     Args:
#         document: Document dict with 'content' and 'metadata'
        
#     Returns:
#         Dict with status, summary, and details
#     """
#     metadata = document.get('metadata', {})
#     content = document.get('content', '')
#     file_type = document.get('file_type', 'unknown')
    
#     diagrams_found = []
    
#     # For DOCX, check metadata
#     if file_type == 'docx':
#         num_images = metadata.get('num_images', 0)
#         num_tables = metadata.get('num_tables', 0)
        
#         if num_images > 0:
#             diagrams_found.append(f'{num_images} images')
#         if num_tables > 0:
#             diagrams_found.append(f'{num_tables} tables')
    
#     # For any document, search for diagram references in text
#     import re
#     figure_patterns = [
#         r'Figure\s+\d+',
#         r'Fig\.\s+\d+',
#         r'Diagram\s+\d+',
#         r'Chart\s+\d+',
#         r'Table\s+\d+'
#     ]
    
#     for pattern in figure_patterns:
#         matches = re.findall(pattern, content, re.IGNORECASE)
#         if matches:
#             diagrams_found.append(f'{len(matches)} {pattern.split()[0]} references')
    
#     if diagrams_found:
#         return {
#             'status': 'found',
#             'summary': f'Found diagrams/figures: {", ".join(diagrams_found)}',
#             'details': {
#                 'diagram_types': diagrams_found,
#                 'count': len(diagrams_found)
#             }
#         }
#     else:
#         return {
#             'status': 'not_found',
#             'summary': 'No diagrams or figures detected',
#             'details': {
#                 'diagram_types': [],
#                 'count': 0
#             }
#         }

def check_diagram(document: dict) -> dict:
    metadata = document.get('metadata', {})
    content = document.get('content', '')
    
    diagrams_found = []
    
    # Check 1: Metadata counts (Reliable for DOCX and PDF)
    imgs = metadata.get('num_images', 0)
    tbls = metadata.get('num_tables', 0)
    vectors = metadata.get('has_vector_graphics', False)
    
    if imgs > 0:
        diagrams_found.append(f"{imgs} images")
    if tbls > 0:
        diagrams_found.append(f"{tbls} tables")
    if vectors:
        diagrams_found.append("vector-based diagrams/charts")
    
    # Check 2: Textual references (Backup for Text/MD files)
    import re
    patterns = {
        'Figure': r'Fig(?:ure|[\.])?\s*\d+',
        'Diagram': r'Diagram\s*\d+',
        'Table': r'Table\s*\d+'
    }
    
    for label, pattern in patterns.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            # We only add text-found labels if we didn't find them in metadata
            unique_count = len(set(matches))
            diagrams_found.append(f"{unique_count} text references to {label}s")

    if diagrams_found:
        return {
            'status': 'found',
            'summary': f"Visuals detected: {', '.join(diagrams_found)}",
            'details': {'found_types': diagrams_found}
        }
    
    return {'status': 'not_found', 'summary': 'No diagrams or tables detected.'}