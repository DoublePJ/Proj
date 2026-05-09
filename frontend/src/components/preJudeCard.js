import { useEffect } from 'react';
import { useLibrary } from '../contexts/LibraryContext';
import Badge from 'react-bootstrap/Badge';
import Card from 'react-bootstrap/Card';
import Stack from 'react-bootstrap/Stack';
import './preActCard.css'; // Reuse existing styles
import { useNavigate } from 'react-router-dom';

function PreJudeCard({ searchTerm = '', selectedTags = [] }) {
    const { judgments, fetchJudgments } = useLibrary();
    const navigate = useNavigate();

    useEffect(() => {
        if (!(judgments || []).length) fetchJudgments().catch(() => {});
    }, [judgments, fetchJudgments]);

    const filterJudgments = (judgmentsList, term, tags) => {
        let filtered = judgmentsList;
        
        // Filter by selectedTags first
        if (tags && tags.length > 0) {
            filtered = filtered.filter(judgment =>
                tags.every(selectedTag => {
                    const tagName = selectedTag.name.toLowerCase();
                    return (judgment.title && judgment.title.toLowerCase().includes(tagName)) ||
                           (judgment.case_number && judgment.case_number.toLowerCase().includes(tagName)) ||
                           (judgment.summary && judgment.summary.toLowerCase().includes(tagName)) ||
                           (judgment.tags && judgment.tags.some(tag => (tag || '').toLowerCase().includes(tagName)));
                })
            );
        }
        
        // Then filter by searchTerm
        if (term && term.trim()) {
            const lower = term.trim().toLowerCase();
            filtered = filtered.filter(judgment =>
                (judgment.title && judgment.title.toLowerCase().includes(lower)) ||
                (judgment.case_number && judgment.case_number.toLowerCase().includes(lower)) ||
                (judgment.summary && judgment.summary.toLowerCase().includes(lower)) ||
                (judgment.tags && judgment.tags.some(tag => (tag || '').toLowerCase().includes(lower)))
            );
        }
        
        return filtered;
    };

    const filteredJudgments = filterJudgments(judgments || [], searchTerm || '', selectedTags);

    return (
        <>
            {filteredJudgments.map((judgment) => (
                <Card key={judgment.id} className="card-act" onClick={() => navigate(`./judgment/${judgment.id}`)}>
                    <Card.Body>
                        <Card.Title>
                            <span className='text-p'>{judgment.title}</span>
                        </Card.Title>
                        {judgment.case_number && (
                            <Card.Subtitle className="mb-2">
                                <span className='text-small-without-color'>คดีหมายเลข: {judgment.case_number}</span>
                            </Card.Subtitle>
                        )}
                        <Stack direction='horizontal' gap={2} className="pre-act-tags-stack">
                            {judgment.tags && judgment.tags.map((tag, index) => (
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

export default PreJudeCard;
