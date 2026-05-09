import { useState, useEffect } from 'react';
import Badge from 'react-bootstrap/Badge';
import Stack from 'react-bootstrap/esm/Stack';
import './SearchBox.css';

function SearchBox({ 
    onAddTag, 
    onRemoveTag, 
    selectedTags = [],
    availableTags = [],
    loading = false,
    placeholder = "ค้นหา...",
    onSearchChange = null
}) {
    const [searchTerm, setSearchTerm] = useState('');
    const [filteredTags, setFilteredTags] = useState([]);

    useEffect(() => {
        if (searchTerm.trim() === '') {
            setFilteredTags([]);
            if (onSearchChange) {
                onSearchChange('');
            }
            return;
        }

        const filtered = (availableTags || []).filter(tag =>
            tag.name.toLowerCase().includes(searchTerm.toLowerCase()) && 
            !selectedTags.some(st => st.id === tag.id)
        );
        setFilteredTags(filtered);

        if (onSearchChange) {
            onSearchChange(searchTerm);
        }
    }, [searchTerm, availableTags, selectedTags, onSearchChange]);

    const handleSearchChange = (event) => {
        setSearchTerm(event.target.value);
    };

    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            const trimmed = (searchTerm || '').trim();
            if (trimmed === '') return;

            const matchingTag = (availableTags || []).find(tag =>
                tag.name.toLowerCase() === trimmed.toLowerCase()
            );

            if (matchingTag) {
                onAddTag(matchingTag);
            } else {
                const textTag = { id: `text-${trimmed}`, name: trimmed, isText: true };
                onAddTag(textTag);
            }
            setSearchTerm('');
            if (onSearchChange) {
                onSearchChange('');
            }
        }
    };

    const handleTagClick = (tag) => {
        onAddTag(tag);
        setSearchTerm('');
        if (onSearchChange) {
            onSearchChange('');
        }
    };

    const handleCustomKeywordClick = () => {
        const trimmed = (searchTerm || '').trim();
        if (trimmed !== '') {
            onAddTag(trimmed);
            setSearchTerm('');
            if (onSearchChange) {
                onSearchChange('');
            }
        }
    };

    return (
        <div className="search-box-container">
            <div className='search-box'>
                <div className='search-input-container'>
                    <span className="material-symbols-outlined">
                        document_search
                    </span>
                    <input 
                        type="search" 
                        placeholder={placeholder}
                        className='text-p'
                        value={searchTerm} 
                        onChange={handleSearchChange} 
                        onKeyDown={handleKeyDown} 
                        disabled={loading} 
                    />
                    <span className="material-symbols-outlined">
                        send
                    </span>
                </div>
                {searchTerm.trim() !== '' && (
                    <ul className='tag-suggestions-list'>
                        {filteredTags.map(tag => (
                            <li 
                                key={tag.id} 
                                onClick={() => handleTagClick(tag)} 
                                style={{ cursor: 'pointer' }}
                            >
                                <span className="text-small">{tag.name}</span>
                            </li>
                        ))}
                        <li 
                            key={"custom-keyword"} 
                            onClick={handleCustomKeywordClick} 
                            style={{ cursor: 'pointer' }}
                        >
                            <span style={{ fontSize: '10px', color: '#A9A9A9' }}>Keyword: </span>
                            <span className="text-small">{searchTerm}</span>
                        </li>
                    </ul>
                )}
            </div>
            {selectedTags.length > 0 && (
                <Stack direction="horizontal" gap={1} className="selected-tags-stack">
                    {selectedTags.map(tag => (
                        <Badge pill bg="info" key={tag.id} className="tag-badge bg-0474ba">
                            <span className="text-small-without-color">{tag.name}</span>
                            <button 
                                onClick={() => onRemoveTag(tag.id)} 
                                style={{ border: 'none', background: 'transparent', cursor: 'pointer', color: '#fff' }}
                            >
                                ✕
                            </button>
                        </Badge>
                    ))}
                </Stack>
            )}
        </div>
    );
}

export default SearchBox;
