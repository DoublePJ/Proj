import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useLibrary } from '../contexts/LibraryContext';
import './preActCard.css';
import Badge from 'react-bootstrap/Badge';
import Card from 'react-bootstrap/Card';
import Stack from 'react-bootstrap/Stack';

function PreActCard({ searchTerm = '', selectedTags = [] }) {
    const navigate = useNavigate();
    const { acts, fetchActs } = useLibrary();

    useEffect(() => {
        if (!(acts || []).length) fetchActs().catch(() => {});
    }, [acts, fetchActs]);

    const filterActs = (actsList, term, tags) => {
        let filtered = actsList;
        
        // Filter by selectedTags first
        if (tags && tags.length > 0) {
            filtered = filtered.filter(act =>
                tags.every(selectedTag => {
                    const tagName = selectedTag.name.toLowerCase();
                    return (act.title && act.title.toLowerCase().includes(tagName)) ||
                           (act.preface && act.preface.toLowerCase().includes(tagName)) ||
                           (act.tags && act.tags.some(tag => (tag || '').toLowerCase().includes(tagName)));
                })
            );
        }
        
        // Then filter by searchTerm
        if (term && term.trim()) {
            const lower = term.trim().toLowerCase();
            filtered = filtered.filter(act =>
                (act.title && act.title.toLowerCase().includes(lower)) ||
                (act.preface && act.preface.toLowerCase().includes(lower)) ||
                (act.tags && act.tags.some(tag => (tag || '').toLowerCase().includes(lower)))
            );
        }
        
        return filtered;
    };

    const filteredActs = filterActs(acts || [], searchTerm || '', selectedTags);

    return (
        <>
            {filteredActs.map((act) => (
                <Card key={act.id} className="card-act" onClick={() => navigate(`./act/${act.id}`)} data-testid={`law-card-act-${act.id}`}>
                    <Card.Body>
                        <Card.Title><span className='text-p'>{act.title}</span></Card.Title>
                        <Stack direction='horizontal' gap={2} className="pre-act-tags-stack">
                            {act.tags.map((tag, index) => (
                                <Badge pill key={index} bg="primary" className="badge-tag">
                                    <span className='text-small-without-color'>{tag}</span>
                                </Badge>
                            ))}
                        </Stack>
                    </Card.Body>
                </Card>
            ))}
        </>
    );
}

export default PreActCard;