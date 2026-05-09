import { useParams, useLocation } from 'react-router-dom';
import { useLibrary } from '../contexts/LibraryContext';
import { useEffect, useRef, useState } from 'react';
import Badge from 'react-bootstrap/Badge';
import Stack from 'react-bootstrap/esm/Stack';
import Leaf from './leaf';
import SearchBox from './SearchBox';
import './laws.css';

function Laws() {
    const params = useParams();
    const location = useLocation();
    const actId = params.actId || params.act;
    const { loading, fetchActById, fetchBooks, fetchTags, setOpenTrail } = useLibrary();
    const [actData, setActData] = useState(null);
    const [filterText, setFilterText] = useState('');
    const [filterTags, setFilterTags] = useState([]);
    const [books, setBooks] = useState([]);
    const [pendingOpenTrail, setPendingOpenTrail] = useState(null);
    const sectionMatchCacheRef = useRef({});
    const autoExpandUsedRef = useRef(false);

    // Combine filterText and filterTags into single search term
    const combinedFilterText = [
        filterText,
        ...filterTags.map(t => t.name)
    ].filter(Boolean).join(' ');

    // Clear cache when filter changes
    useEffect(() => {
        sectionMatchCacheRef.current = {};
    }, [combinedFilterText]);

    useEffect(() => {
        let mounted = true;
        if (!actId) return;

        // โหลด tags ก่อนเพื่อให้ act มี tag names ที่ถูกต้อง
        fetchTags().finally(() => {
            fetchActById(actId)
                .then((act) => { if (mounted) setActData(act) })
                .catch((error) => { console.error('Error fetching act:', error); });
            fetchBooks(actId)
                .then((booksData) => {
                    if (mounted) {
                        setBooks(booksData || []);
                    }
                })
                .catch((error) => { console.error('Error fetching books:', error); });
        });

        return () => { mounted = false; };
    }, [actId, fetchActById, fetchBooks, fetchTags]);

    // เก็บ openTrail จาก navigation state ไว้ก่อน
    useEffect(() => {
        if (location.state?.openTrail) {
            setPendingOpenTrail(location.state.openTrail);
        }
    }, [location.state]);

    // Apply openTrail หลังจาก books โหลดเสร็จแล้ว
    useEffect(() => {
        if (pendingOpenTrail && books.length > 0) {
            setOpenTrail(pendingOpenTrail);
            setPendingOpenTrail(null);
        }
    }, [pendingOpenTrail, books, setOpenTrail]);

    // one-time auto-expand consumer for top-level books
    const consumeAutoExpand = () => {
        if (books.length === 1 && !autoExpandUsedRef.current) {
            autoExpandUsedRef.current = true;
            return true;
        }
        return false;
    };

    // reset one-time auto-expand when switching acts
    useEffect(() => {
        autoExpandUsedRef.current = false;
    }, [actId]);

    const handleAddFilterTag = (tag) => {
        if (typeof tag === 'string') {
            // Add as a tag (badge)
            const textTag = { id: `text-${tag}`, name: tag, isText: true };
            setFilterTags(prev => [...prev, textTag]);
            setFilterText('');
        } else {
            setFilterTags(prev => [...prev, tag]);
            setFilterText('');
        }
    };

    const handleRemoveFilterTag = (tagId) => {
        setFilterTags(prev => prev.filter(t => t.id !== tagId));
    };

    const handleSearchChange = (text) => {
        setFilterText(text);
    };

    return (
        <>
            {!actData && !loading && (
                <div className='laws-no-data'>
                    <span className='text-p-without-color'>ไม่พบข้อมูลพระราชบัญญัติที่เลือก</span>
                </div>
            )}

            {actData && (
                <section>
                    <div className='laws-header'>
                        <span className='laws-title text-h1'>{actData.title}</span>
                        <Stack direction="horizontal" gap={1} className="tags-stack">
                            {actData.tags.map(tag => (
                                <Badge pill bg="info" key={tag.id} className="tag-badge bg-0474ba">
                                    <span className="text-small-without-color">{tag}</span>
                                </Badge>
                            ))}
                        </Stack>
                    </div>

                    <SearchBox
                        onAddTag={handleAddFilterTag}
                        onRemoveTag={handleRemoveFilterTag}
                        selectedTags={filterTags}
                        availableTags={[]}
                        loading={loading}
                        placeholder="ค้นหาในพระราชบัญญัติ..."
                        onSearchChange={handleSearchChange}
                    />

                    {books.length > 0 && (
                        <div className='laws-structure'>
                            {books.map(book => (
                                <Leaf
                                    key={book.id}
                                    depth={0}
                                    item={book}
                                    type="book"
                                    filterText={combinedFilterText}
                                    sectionMatchCache={sectionMatchCacheRef.current}
                                    autoExpandConsumer={consumeAutoExpand}
                                />
                            ))}
                        </div>
                    )}

                    {books.length === 0 && !loading && (
                        <div className='laws-no-books'>
                            <span className="text-p-without-color">ไม่พบข้อมูลโครงสร้างของพระราชบัญญัตินี้</span>
                        </div>
                    )}

                </section>
            )}
        </>
    );
}

export default Laws;