from typing import List, Dict, Any

def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 100) -> List[str]:
    """
    Splits text recursively using a list of separators: double newlines, single newlines, spaces,
    and finally characters if needed. Ensures chunks are within chunk_size while maintaining overlap.
    """
    separators = ["\n\n", "\n", " ", ""]
    
    def _split(text_to_split: str, current_separators: List[str]) -> List[str]:
        if len(text_to_split) <= chunk_size:
            return [text_to_split]
            
        if not current_separators:
            # Fallback to hard character chunking if no separators left
            return [text_to_split[i:i+chunk_size] for i in range(0, len(text_to_split), chunk_size - chunk_overlap)]
            
        separator = current_separators[0]
        next_separators = current_separators[1:]
        
        # Split text by the separator
        if separator == "":
            splits = list(text_to_split)
        else:
            splits = text_to_split.split(separator)
            
        chunks = []
        current_chunk = ""
        
        for part in splits:
            # Reconstruct the separator if we split by it
            part_str = part + (separator if separator != "" else "")
            
            # If a single part is larger than the chunk size, split it recursively
            if len(part_str) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                sub_chunks = _split(part_str, next_separators)
                chunks.extend(sub_chunks)
            else:
                # If adding this part exceeds chunk_size, flush the current chunk
                if len(current_chunk) + len(part_str) > chunk_size:
                    if current_chunk:
                        chunks.append(current_chunk)
                    # Seeding the next chunk with overlap from the end of the current chunk
                    if chunk_overlap > 0 and len(current_chunk) > chunk_overlap:
                        overlap_start = max(0, len(current_chunk) - chunk_overlap)
                        current_chunk = current_chunk[overlap_start:]
                    else:
                        current_chunk = ""
                current_chunk += part_str
                
        if current_chunk:
            chunks.append(current_chunk)
            
        # Clean up whitespace and empty chunks
        final_chunks = []
        for c in chunks:
            c_stripped = c.strip()
            if c_stripped:
                final_chunks.append(c_stripped)
        return final_chunks

    return _split(text, separators)


def chunk_kb_article(kb_id: int, category: str, title: str, content: str, chunk_size: int = 500, chunk_overlap: int = 100) -> List[Dict[str, Any]]:
    """
    Applies split_text to a KB article's content and formats each chunk with metadata.
    """
    raw_chunks = split_text(content, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    chunks_data = []
    for idx, chunk_content in enumerate(raw_chunks):
        # Keep chunk content clean so customer-facing replies are clean of raw metadata labels
        formatted_content = chunk_content
        
        chunks_data.append({
            "kb_id": kb_id,
            "chunk_index": idx,
            "content": formatted_content,
            "metadata_json": {
                "category": category,
                "title": title,
                "original_chunk_length": len(chunk_content)
            }
        })
    return chunks_data
