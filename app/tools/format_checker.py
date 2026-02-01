def check_format(document: dict) -> dict:
    """
    Comprehensive document format and structure validation.
    
    Checks:
    - Document structure (sections, headings)
    - Required sections (based on document type)
    - Formatting consistency
    - Content organization
    - Metadata completeness
    
    Args:
        document: Document dict with 'content' and 'metadata'
        
    Returns:
        Dict with status, summary, and detailed validation results
    """
    content = document.get('content', '')
    metadata = document.get('metadata', {})
    file_type = document.get('file_type', 'unknown')
    
    validations = []
    warnings = []
    errors = []
    
    # ========================================================================
    # 1. BASIC STRUCTURE CHECKS
    # ========================================================================
    
    # Check if document has sufficient content
    word_count = len(content.split())
    if word_count < 50:
        errors.append(f'Document is too short ({word_count} words)')
    elif word_count < 200:
        warnings.append(f'Document is relatively short ({word_count} words)')
    else:
        validations.append(f'Document has sufficient content ({word_count} words)')
    
    # Check for sections/headings
    sections = metadata.get('sections', [])
    if not sections:
        errors.append('No clear document structure/sections found')
    elif len(sections) < 3:
        warnings.append(f'Only {len(sections)} sections found - document may lack structure')
    else:
        validations.append(f'Document has {len(sections)} sections/headings')
    
    # ========================================================================
    # 2. REQUIRED SECTIONS CHECK
    # ========================================================================
    
    # Common required sections for technical/business documents
    required_sections = {
        'overview': ['overview', 'executive summary', 'abstract'],
        'introduction': ['introduction', 'background'],
        'methodology': ['methodology', 'approach', 'methods', 'implementation'],
        'results': ['results', 'findings', 'outcomes'],
        'conclusion': ['conclusion', 'summary', 'closing']
    }
    
    sections_lower = [s.lower() for s in sections]
    found_required = {}
    
    for category, keywords in required_sections.items():
        found = False
        for keyword in keywords:
            if any(keyword in section for section in sections_lower):
                found = True
                found_required[category] = True
                break
        
        if found:
            validations.append(f'✓ Found {category} section')
        else:
            warnings.append(f'⚠ Missing {category} section')
            found_required[category] = False
    
    # ========================================================================
    # 3. CONTENT ORGANIZATION CHECKS
    # ========================================================================
    
    # Check if sections are in logical order
    expected_order = ['overview', 'introduction', 'methodology', 'results', 'conclusion']
    section_positions = {}
    
    for i, section in enumerate(sections_lower):
        for category in expected_order:
            if any(keyword in section for keyword in required_sections[category]):
                section_positions[category] = i
                break
    
    # Verify order
    if len(section_positions) >= 2:
        positions = [section_positions.get(cat, -1) for cat in expected_order if cat in section_positions]
        if positions == sorted(positions):
            validations.append('Sections follow logical order')
        else:
            warnings.append('Sections may not be in standard order')
    
    # ========================================================================
    # 4. FORMATTING CONSISTENCY CHECKS
    # ========================================================================
    
    # Check for consistent heading styles
    heading_lengths = [len(s) for s in sections]
    if heading_lengths:
        avg_length = sum(heading_lengths) / len(heading_lengths)
        if all(10 <= length <= 100 for length in heading_lengths):
            validations.append('Heading lengths are consistent')
        else:
            warnings.append('Some headings are unusually long or short')
    
    # Check for numbered sections
    import re
    numbered_sections = [s for s in sections if re.match(r'^\d+\.', s.strip())]
    if len(numbered_sections) > len(sections) / 2:
        validations.append('Document uses numbered sections')
    
    # ========================================================================
    # 5. FILE-TYPE SPECIFIC CHECKS
    # ========================================================================
    
    if file_type == 'pdf':
        num_pages = metadata.get('num_pages', 0)
        if num_pages == 0:
            errors.append('PDF has no pages')
        elif num_pages < 2:
            warnings.append('PDF has only 1 page - may be incomplete')
        else:
            validations.append(f'PDF has {num_pages} pages')
    
    elif file_type == 'docx':
        num_tables = metadata.get('num_tables', 0)
        num_images = metadata.get('num_images', 0)
        
        if num_tables > 0:
            validations.append(f'Document contains {num_tables} table(s)')
        if num_images > 0:
            validations.append(f'Document contains {num_images} image(s)')
        
        num_paragraphs = metadata.get('num_paragraphs', 0)
        if num_paragraphs < 5:
            warnings.append('Document has very few paragraphs')
        else:
            validations.append(f'Document has {num_paragraphs} paragraphs')
    
    # ========================================================================
    # 6. CONTENT QUALITY CHECKS
    # ========================================================================
    
    # Check for placeholder text
    placeholders = ['lorem ipsum', 'todo', 'tbd', 'xxx', '[insert', 'placeholder']
    found_placeholders = [p for p in placeholders if p in content.lower()]
    if found_placeholders:
        warnings.append(f'Found placeholder text: {", ".join(found_placeholders)}')
    
    # Check for empty sections (multiple consecutive line breaks)
    empty_sections = content.count('\n\n\n\n')
    if empty_sections > 3:
        warnings.append(f'Document has {empty_sections} potentially empty sections')
    
    # ========================================================================
    # 7. COMPLETENESS SCORE
    # ========================================================================
    
    total_checks = len(validations) + len(warnings) + len(errors)
    completeness_score = (len(validations) / total_checks * 100) if total_checks > 0 else 0
    
    # ========================================================================
    # DETERMINE STATUS
    # ========================================================================
    
    if len(errors) > 0:
        status = 'invalid'
        summary = f'Format validation failed: {len(errors)} error(s), {len(warnings)} warning(s)'
    elif len(warnings) > 3:
        status = 'needs_improvement'
        summary = f'Format acceptable but has {len(warnings)} warning(s) - completeness: {completeness_score:.0f}%'
    else:
        status = 'valid'
        summary = f'Format validation passed - completeness: {completeness_score:.0f}%'
    
    return {
        'status': status,
        'summary': summary,
        'details': {
            'validations': validations,
            'warnings': warnings,
            'errors': errors,
            'file_type': file_type,
            'word_count': word_count,
            'section_count': len(sections),
            'required_sections_found': found_required,
            'completeness_score': round(completeness_score, 1),
            'total_checks': total_checks
        }
    }