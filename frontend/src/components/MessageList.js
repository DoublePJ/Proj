import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { useLibrary } from '../contexts/LibraryContext';
import './MessageList.css';

function MessageList({ messages }) {
    const messagesEndRef = useRef(null);
    const navigate = useNavigate();
    const { fetchSectionsByActAndNumber, setOpenTrail } = useLibrary();
    const [openMetadataId, setOpenMetadataId] = useState(null);

    // Auto scroll ไปด้านล่างเมื่อมีข้อความใหม่
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const toggleMetadata = (messageId) => {
        setOpenMetadataId(prev => (prev === messageId ? null : messageId));
    };

    // ฟังก์ชันสำหรับจัดการคลิกลิงก์มาตรา
    const handleSectionClick = async (sectionNumber, actId) => {
        try {
            // ดึงข้อมูล section จาก API
            const sections = await fetchSectionsByActAndNumber(actId, sectionNumber);
            let target = Array.isArray(sections) ? sections[0] : sections;

            if (!target || !target.id) {
                console.error('Section not found');
                return;
            }

            // Navigate ไปหน้า library พร้อม state
            navigate(`/library/act/${actId}`, {
                state: {
                    openTrail: {
                        actId: actId,
                        bookId: target.book_id,
                        groupId: target.group_id,
                        superId: target.super_id,
                        sectionId: target.id,
                    }
                }
            });

            // Set openTrail ใน context ด้วย
            setOpenTrail({
                actId: actId,
                bookId: target.book_id,
                groupId: target.group_id,
                superId: target.super_id,
                sectionId: target.id,
            });
        } catch (error) {
            console.error('Error navigating to section:', error);
        }
    };

    // ฟังก์ชันสำหรับจัดการคลิกลิงก์คำพิพากษา
    const handleJudgmentClick = (judgmentId) => {
        try {
            navigate(`/library/judgment/${judgmentId}`);
        } catch (error) {
            console.error('Error navigating to judgment:', error);
        }
    };

    // ฟังก์ชันแปลงข้อความให้มีลิงก์มาตรา
    const renderMessageWithSectionLinks = (text, metadata) => {
        let processedText = text.replace(
            /\[([^\]]+)\]\{judgment_id=([^}]+)\}/g,
            (match, textContent, judgmentIdRaw) => {
                const judgmentId = judgmentIdRaw.trim();
                if (!/^\d+$/.test(judgmentId)) {
                    return textContent;
                }
                return `[${textContent}](#judgment-${judgmentId})`;
            }
        );

        processedText = processedText.replace(
            /\[([^\]]+)\]\{act_id=([^,}]+),\s*sec_num=([^}]+)\}/g,
            (match, textContent, actIdRaw, secNumRaw) => {
                const actId = actIdRaw.trim();
                const secNum = secNumRaw.trim();
                if (!/^\d+$/.test(actId) || !/^\d+$/.test(secNum)) {
                    return textContent;
                }
                return `[${textContent}](#section-${secNum}-${actId})`;
            }
        );
        // เพิ่ม metadata fallback
        if (!metadata || !metadata.sections || metadata.sections.length === 0) {
            return <ReactMarkdown>{processedText}</ReactMarkdown>;
        }
        

        // Custom components สำหรับ ReactMarkdown
        const components = {
            a: ({ node, href, children, ...props }) => {
                // ตรวจสอบรูปแบบคำพิพากษา [text](#judgment-9876)
                const judgmentMatch = href?.match(/#judgment-(\d+)/);
                if (judgmentMatch) {
                    const judgmentId = judgmentMatch[1];
                    return (
                        <button
                            onClick={(e) => {
                                e.preventDefault();
                                handleJudgmentClick(judgmentId);
                            }}
                            className="button-link-section"
                            title={`ดูคำพิพากษา ${judgmentId}`}
                            {...props}
                        >
                            {children}
                        </button>
                    );
                }

                // ตรวจสอบรูปแบบใหม่ [text](#section-Y-X)
                const newFormatMatch = href?.match(/#section-(\d+[ก-ฮ]?)-(\d+)/);
                if (newFormatMatch) {
                    const sectionNumber = newFormatMatch[1];
                    const actId = newFormatMatch[2];
                    return (
                        <button
                            onClick={(e) => {
                                e.preventDefault();
                                handleSectionClick(sectionNumber, actId);
                            }}
                            className="button-link-section"
                            title={`ไปที่มาตรา ${sectionNumber}`}
                            {...props}
                        >
                            {children}
                        </button>
                    );
                }

                return <a href={href} target="_blank" rel="noopener noreferrer" {...props}>{children}</a>;
            }
        };

        return <ReactMarkdown components={components}>{processedText}</ReactMarkdown>;
    };

    return (
        <div className="chat-messages">
            {messages.length === 0 ? (
                <div className="chat-empty">
                    <div className="empty-icon">💬</div>
                    <span className="text-h3-without-color" style={{ display: 'block' }}>ยินดีต้อนรับ!</span>
                    <span className="text-p-without-color">ถามคำถามใดๆ เกี่ยวกับกฎหมายแรงงานไทย</span>
                </div>
            ) : (
                messages.map(msg => {
                    const isMetadataOpen = openMetadataId === msg.id;
                    const actId = msg.metadata?.acts?.[0];
                    const actIdNum = Array.isArray(actId) ? actId[0] : actId;
                    const uniqueSections = Array.isArray(msg.metadata?.sections)
                        ? Array.from(
                            new Map(
                                msg.metadata.sections.map((section) => {
                                    const sectionNum = typeof section === 'object' ? section.section_number : section;
                                    const paragraphValue = typeof section === 'object' ? section.paragraph_number : '';
                                    const uniqueKey = `${String(sectionNum ?? '').trim()}-${String(paragraphValue ?? '').trim()}`;
                                    return [uniqueKey, { sectionNum, paragraphValue }];
                                })
                            ).values()
                        ).filter(({ sectionNum }) => sectionNum !== undefined && sectionNum !== null && String(sectionNum).trim() !== '')
                        : [];
                    return (
                        <div key={msg.id} className={`chat-message ${msg.type}`}>
                            <div className="message-bubble">
                                {renderMessageWithSectionLinks(msg.text, msg.metadata)}

                                {msg.isLoading && (
                                    <div className="typing-indicator">
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                    </div>
                                )}

                                {msg.metadata && !msg.isLoading && (
                                    <div className={`message-metadata ${isMetadataOpen ? 'expanded' : ''}`}>
                                        <button
                                            type="button"
                                            className="metadata-toggle"
                                            onClick={() => toggleMetadata(msg.id)}
                                            aria-expanded={isMetadataOpen}
                                        >
                                            <span className='material-symbols-outlined close'>book_2</span>
                                            <span className='material-symbols-outlined open'>menu_book</span>
                                            <span className='text-p-without-color'><strong>แหล่งอ้างอิง</strong></span>
                                        </button>
                                        {isMetadataOpen && (
                                            <>
                                                {msg.metadata.acts && msg.metadata.acts.length > 0 && (
                                                    <div className="metadata-section">
                                                        <div className="metadata-header">
                                                            <span className="material-symbols-outlined">book</span>
                                                            <span className='text-small-without-color'><strong>พระราชบัญญัติที่เกี่ยวข้อง</strong></span>
                                                        </div>
                                                        <div className="metadata-content">
                                                            {msg.metadata.acts.map((act, idx) => {
                                                                const actName = Array.isArray(act) ? act[1] : `พระราชบัญญัติ ${act}`;
                                                                return (
                                                                    <div key={idx} className="act-item">
                                                                        <span className="small act-name">{actName}</span>
                                                                    </div>
                                                                );
                                                            })}
                                                        </div>
                                                    </div>
                                                )}
                                                {uniqueSections.length > 0 && (
                                                    <div className="metadata-section">
                                                        <div className="metadata-header">
                                                            <span className="material-symbols-outlined">gavel</span>
                                                            <span className='text-small-without-color'><strong>มาตราที่เกี่ยวข้อง</strong></span>
                                                        </div>
                                                        <div className="metadata-content">
                                                            <div className="sections-list">
                                                                {uniqueSections.map(({ sectionNum, paragraphValue }, idx) => {
                                                                    const paragraphNum = paragraphValue ? `วรรค ${paragraphValue}` : '';
                                                                    return (
                                                                        <span
                                                                            key={idx}
                                                                            className="small section-badge"
                                                                            onClick={() => handleSectionClick(String(sectionNum), actIdNum)}
                                                                            title="คลิกเพื่อดูรายละเอียด"
                                                                        >
                                                                            มาตรา {sectionNum} {paragraphNum}
                                                                        </span>
                                                                    );
                                                                })}
                                                            </div>
                                                        </div>
                                                    </div>
                                                )}
                                                {msg.metadata.judgments && msg.metadata.judgments.length > 0 && (
                                                    <div className="metadata-section">
                                                        <div className="metadata-header">
                                                            <span className="material-symbols-outlined">gavel</span>
                                                            <span className='text-small-without-color'><strong>คำพิพากษาที่เกี่ยวข้อง</strong></span>
                                                        </div>
                                                        <div className="metadata-content">
                                                            <div className="sections-list">
                                                                {msg.metadata.judgments.map((judgment, idx) => {
                                                                    const judgmentId = judgment.id;
                                                                    return (
                                                                        <span
                                                                            key={idx}
                                                                            className="small section-badge"
                                                                            onClick={() => handleJudgmentClick(judgmentId)}
                                                                            title="คลิกเพื่อดูรายละเอียด"
                                                                        >
                                                                            {judgment.title}
                                                                        </span>
                                                                    );
                                                                })}
                                                            </div>
                                                        </div>
                                                    </div>
                                                )}
                                            </>
                                        )}
                                    </div>
                                )}
                            </div>
                            <div className="message-time">
                                {msg.timestamp.toLocaleTimeString('th-TH', {
                                    hour: '2-digit',
                                    minute: '2-digit'
                                })}
                            </div>
                        </div>
                    );
                })
            )}
            <div ref={messagesEndRef} />
        </div>
    );
}

export default MessageList;
