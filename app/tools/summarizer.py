def summarize_content(document: dict) -> dict:
    """
    Summarize document content.
    
    Args:
        document: Document dict with 'content' and 'metadata'
        
    Returns:
        Dict with status, summary, and details
    """
    content = document.get('content', '')
    metadata = document.get('metadata', {})
    sections = metadata.get('sections', [])
    
    # Get first few paragraphs as summary
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
    if not paragraphs:
        return {
            'status': 'error',
            'summary': 'Unable to summarize - no content found',
            'details': {}
        }
    
    # Create a simple summary
    summary_parts = []
    
    if sections:
        summary_parts.append(f'Document has {len(sections)} main sections')
        summary_parts.append(f'Sections include: {", ".join(sections[:5])}')
    
    # Get first paragraph as overview
    first_para = paragraphs[0][:500] if paragraphs else ''
    
    word_count = len(content.split())
    
    return {
        'status': 'success',
        'summary': f'Document summary generated ({word_count} words total)',
        'details': {
            'structure': ', '.join(summary_parts),
            'preview': first_para,
            'word_count': word_count,
            'paragraph_count': len(paragraphs)
        }
    }