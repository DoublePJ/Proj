import { useEffect, useState } from 'react';
import './pageLibrary.css';
import PreActCard from '../components/preActCard';
import SearchBox from '../components/SearchBox';
import { useLibrary } from '../contexts/LibraryContext';
import PreJudeCard from '../components/preJudeCard';

function PageLibrary() {
    const { fetchTags, tags, selectedTags, addTag, removeTag, searchTerm, setSearchTerm } = useLibrary();
    const [loading, setLoading] = useState(true);


    useEffect(() => {
        let alive = true;
        setLoading(true);
        // fetch only tags here (acts will load when Acts mounts)
        fetchTags().finally(() => { if (alive) setLoading(false); });
    }, [fetchTags]);


    return (
        <main className="library-content" data-testid="library-page">
            <div className='text-h1' data-testid="library-page-title">
                ยินดีต้อนรับสู่ห้องสมุดกฎหมาย
            </div>
            <SearchBox
                onAddTag={addTag}
                onRemoveTag={removeTag}
                selectedTags={selectedTags}
                availableTags={tags}
                loading={loading}
                placeholder="ค้นหากฎหมาย..."
                onSearchChange={setSearchTerm}
            />
            <main className="pre-content">
                <PreActCard searchTerm={searchTerm} selectedTags={selectedTags} />
                <PreJudeCard searchTerm={searchTerm} selectedTags={selectedTags} />
            </main>
        </main>
    );
}

export default PageLibrary;