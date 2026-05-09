import { useEffect, useRef, useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { useLibrary } from '../contexts/LibraryContext';
import Badge from 'react-bootstrap/Badge';
import Stack from 'react-bootstrap/Stack';
import './judg.css';
import SearchBox from './SearchBox';

function Jude() {
    const params = useParams();
    const location = useLocation();
    const judgId = params.judgment_id || params.act;
    const { loading, fetchJudgmentById, fetchTags, setOpenTrail } = useLibrary();
    const [judgmentData, setJudgmentData] = useState(null);
    const [filterText, setFilterText] = useState('');
    const [filterTags, setFilterTags] = useState([]);
    const [pendingOpenTrail, setPendingOpenTrail] = useState(null);
    const [toggleRelatedLaw, setToggleRelatedLaw] = useState(false);
    const sectionMatchCacheRef = useRef({});

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
        if (!judgId) return;

        // โหลด tags ก่อนเพื่อให้ act มี tag names ที่ถูกต้อง
        fetchTags().finally(() => {
            fetchJudgmentById(judgId)
                .then((judgment) => { if (mounted) setJudgmentData(judgment) })
                .catch((error) => { console.error('Error fetching judgment:', error); });
        });

        return () => { mounted = false; };
    }, [judgId, fetchJudgmentById, fetchTags]);

    // เก็บ openTrail จาก navigation state ไว้ก่อน
    useEffect(() => {
        if (location.state?.openTrail) {
            setPendingOpenTrail(location.state.openTrail);
        }
    }, [location.state]);

    // Apply openTrail หลังจาก judgment โหลดเสร็จแล้ว
    useEffect(() => {
        if (pendingOpenTrail && judgmentData) {
            setOpenTrail(pendingOpenTrail);
            setPendingOpenTrail(null);
        }
    }, [pendingOpenTrail, judgmentData, setOpenTrail]);
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

    const highlightText = (text, searchTerm) => {
        if (!searchTerm || !text) return text;
        const parts = text.split(new RegExp(`(${searchTerm})`, 'gi'));
        return parts.map((part, i) =>
            part.toLowerCase() === searchTerm.toLowerCase()
                ? <mark key={i} style={{ backgroundColor: '#ffeb3b', padding: '2px 0' }}>{part}</mark>
                : part
        );
    };

    const displaySummaryJudgment = (judgment) => {
        if (!judgment) return null;
        const listJudgment = judgment.split('\n').filter(line => line.trim() !== '');
        return (
            <div>
                <span className='text-h1'>สรุปคดี</span>
                {listJudgment.map((line, index) => (
                    <p key={index} style={{ textAlign: "left" }}>
                        <span style={{ marginLeft: '2rem' }} />{highlightText(line, combinedFilterText)}
                    </p>
                ))}
            </div>
        );
    };

    const displayJudgment = (judgment) => {
        if (!judgment) return null;
        const listJudgment = judgment.split('\n').filter(line => line.trim() !== '');
        
        let relatedLaws = [];
        let contentStartIndex = 2;
        let relateTitle = null;
        while (contentStartIndex < listJudgment.length) {
            if (listJudgment[contentStartIndex].includes('กฎหมายที่เกี่ยวข้อง')) {
                relateTitle = listJudgment[contentStartIndex].trim();
            } else if (listJudgment[contentStartIndex].startsWith('พระราชบัญญัติ')
                || listJudgment[contentStartIndex].match(/^พ\.?ร\.?บ\.?/) ) {
                relatedLaws.push(listJudgment[contentStartIndex]);
            } else {
                break;
            }
            contentStartIndex += 1;
        }
        return (
            <div>
                <span className='text-h1'>{highlightText(listJudgment[0], combinedFilterText)}</span>
                {relateTitle &&
                    <div className={`text-h3 ${toggleRelatedLaw ? 'toggle-on' : 'toggle-off'}`}
                    onClick={() => setToggleRelatedLaw(!toggleRelatedLaw)}>{highlightText(relateTitle, combinedFilterText)}
                    </div>
                }
                {relateTitle && toggleRelatedLaw && relatedLaws.length > 0 && (
                    <div>
                        {relatedLaws.map((law, index) => (
                            <p key={index} className='text-p' style={{ textAlign: "left"}}>{highlightText(law, combinedFilterText)}</p>
                        ))}
                    <br />
                    </div>
                )}
                {listJudgment.slice(contentStartIndex).map((line, index) => (
                    <p key={index} style={{ textAlign: "left" }}>
                        <span style={{ marginLeft: '2rem' }} />{highlightText(line, combinedFilterText)}
                    </p>
                ))}
            </div>
        );
    }

    return (
        <>
            {!judgmentData && !loading && (
                <div className='laws-no-data'>
                    <span className='text-p-without-color'>ไม่พบข้อมูลคดีที่เลือก</span>
                </div>
            )}

            {judgmentData && (
                <section>
                    <div className='laws-header'>
                        <span className='laws-title text-h1'>{judgmentData.title}</span>
                        <br></br>
                        <span className='text-h3-without-color'>คดีหมายเลข: {judgmentData.case_number}</span>
                        <Stack direction="horizontal" gap={1} className="tags-stack">
                            {judgmentData.tags.map(tag => (
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
                        placeholder="ค้นหาในคดี..."
                        onSearchChange={handleSearchChange}
                    />

                    {/* เนื้อหาของคดีจะแสดงในส่วนนี้ */}
                    <div className='judgment-container'>
                        {displaySummaryJudgment(judgmentData.summary)}
                        {/* ส่วนนี้จะเป็นรายละเอียดของคดี เช่น เหตุการณ์, คำพิพากษา, ฯลฯ */}
                        {displayJudgment(judgmentData.detail)}
                    </div>
                </section>
            )}
        </>
    );
}

export default Jude;