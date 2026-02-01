def search_headings(document: dict) -> dict:
    """
    Search for headings/sections in the document.
    
    Args:
        document: Document dict with 'content' and 'metadata'
        
    Returns:
        Dict with status, summary, and details
    """
    sections = document.get('metadata', {}).get('sections', [])
    content = document.get('content', '')
    
    if not sections:
        # Try to extract from content if metadata doesn't have sections
        import re
        lines = content.split('\n')
        sections = []
        for line in lines[:100]:  # Check first 100 lines
            if line.strip().isupper() and 5 < len(line.strip()) < 100:
                sections.append(line.strip())
    
    if sections:
        return {
            'status': 'found',
            'summary': f'Found {len(sections)} sections/headings',
            'details': {
                'sections': sections,
                'count': len(sections)
            }
        }
    else:
        return {
            'status': 'not_found',
            'summary': 'No clear sections/headings found',
            'details': {
                'sections': [],
                'count': 0
            }
        }
