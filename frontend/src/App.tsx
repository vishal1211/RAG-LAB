import { useEffect, useRef, useState } from 'react';
import type { ReactNode } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './App.css';

type Source = { filename: string | null; page: number | null; content: string; distance: number };
type ChatMessage = { role: 'user' | 'assistant'; content: string; sources?: Source[]; error?: boolean };
type Document = { name: string; size: number; hash: string };
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

function Icon({ name, size = 20 }: { name: string; size?: number }) {
  const paths: Record<string, ReactNode> = {
    book: <><path d="M4 4h6a3 3 0 0 1 2 1 3 3 0 0 1 2-1h6v15h-6a3 3 0 0 0-2 1 3 3 0 0 0-2-1H4z" /><path d="M12 5v15" /></>,
    plus: <path d="M12 5v14M5 12h14" />,
    upload: <><path d="M12 16V3m-5 5 5-5 5 5M4 15v5h16v-5" /></>,
    file: <><path d="M14 3H5v18h14V8zM14 3v5h5M8 12h8M8 16h6" /></>,
    arrow: <path d="M12 19V5m-6 6 6-6 6 6" />,
    sparkle: <><path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5z" /></>,
    chat: <path d="M20 15a3 3 0 0 1-3 3H9l-5 3V6a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3z" />,
    check: <path d="m5 12 4 4L19 6" />,
    chevron: <path d="m9 5 7 7-7 7" />,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name] ?? paths.file}</svg>;
}

function App() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID());
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploadError, setUploadError] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);
  const queryInput = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (messages.length) messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, [messages, isLoading]);

  async function uploadFile(file?: File) {
    if (!file || isUploading) return;
    setUploadError(false);
    if (file.type !== 'application/pdf') {
      setUploadError(true);
      setUploadStatus('Please choose a PDF file.');
      return;
    }
    setIsUploading(true);
    setUploadStatus(`Processing ${file.name}…`);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch(`${API_BASE_URL}/upload/file`, { method: 'POST', body: formData });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Upload failed. Please try again.');
      setDocuments(previous => previous.some(doc => doc.hash === data.file_hash) ? previous : [...previous, { name: data.filename ?? file.name, size: file.size, hash: data.file_hash ?? file.name }]);
      setUploadStatus(data.duplicate ? `${data.filename} is already in your knowledge base.` : `${data.filename} is ready to explore.`);
    } catch (error) {
      setUploadError(true);
      setUploadStatus(error instanceof Error ? error.message : 'Unable to upload. Please try again.');
    } finally {
      setIsUploading(false);
      if (fileInput.current) fileInput.current.value = '';
    }
  }

  async function askQuestion() {
    if (!query.trim() || isLoading) return;
    const currentQuery = query.trim();
    setQuery('');
    setIsLoading(true);
    setMessages(previous => [...previous, { role: 'user', content: currentQuery }]);
    try {
      const response = await fetch(`${API_BASE_URL}/upload/search`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: currentQuery, session_id: sessionId }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Failed to get an answer. Please try again.');
      setMessages(previous => [...previous, { role: 'assistant', content: data.answer, sources: data.sources ?? [] }]);
    } catch (error) {
      setMessages(previous => [...previous, { role: 'assistant', error: true, content: error instanceof Error ? error.message : 'Unable to connect. Please try again.' }]);
      setQuery(currentQuery);
    } finally { setIsLoading(false); }
  }


  return <div className="app-shell">
    <aside className="sidebar" aria-label="Document workspace">
      <a className="brand" href="./"><span className="brand-mark"><Icon name="book" size={23} /></span>rag<span className="brand-light">lab</span><span className="brand-dot" /></a>
      <div className="workspace-label">YOUR WORKSPACE</div>
      <button className="new-chat" disabled={isLoading} onClick={() => { setMessages([]); setSessionId(crypto.randomUUID()); setQuery(''); queryInput.current?.focus(); }}><Icon name="plus" />New conversation<span className="new-chat-arrow">↗</span></button>
      <div className="section-label"><span>KNOWLEDGE BASE</span><span className="count">{documents.length}</span></div>
      <input ref={fileInput} id="pdf-upload" className="visually-hidden" type="file" accept="application/pdf" disabled={isUploading} onChange={event => void uploadFile(event.target.files?.[0])} />
      <button className={`upload-zone ${dragging ? 'dragging' : ''}`} disabled={isUploading} onClick={() => fileInput.current?.click()} onDragOver={event => { event.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={event => { event.preventDefault(); setDragging(false); void uploadFile(event.dataTransfer.files[0]); }}>
        <span className="upload-icon"><Icon name="upload" size={22} /></span>
        <strong>{isUploading ? 'Adding to your knowledge…' : 'Drop your PDF here'}</strong>
        <span>{isUploading ? 'This may take a moment' : <>or <b>browse files</b> to upload</>}</span>
        <small>PDF documents</small>
      </button>
      <p className={`upload-status ${uploadError ? 'error' : ''}`} role="status">{uploadStatus}</p>
      <div className="document-list">
        {documents.length ? <><p className="list-caption">Added in this visit</p>{documents.map(doc => <div className="document" key={doc.hash}><span className="pdf-icon"><Icon name="file" /></span><div><strong title={doc.name}>{doc.name}</strong><small>{doc.size < 1024 * 1024 ? `${Math.ceil(doc.size / 1024)} KB` : `${(doc.size / (1024 * 1024)).toFixed(1)} MB`} · Ready</small></div><span className="ready-check"><Icon name="check" size={15} /></span></div>)}</> : <div className="no-documents"><Icon name="file" size={19} /><p>Your knowledge starts here.<br />Add a document to get started.</p></div>}
      </div>
      <div className="sidebar-tip"><span className="tip-heading"><Icon name="sparkle" size={17} />A little context goes a long way</span><p>Ask specific questions to find useful insights in your documents.</p></div>
      <div className="workspace-footer"><span className="avatar">W</span><div><strong>My workspace</strong><small>Document intelligence</small></div><span className="footer-dot" /></div>
    </aside>

    <main className="main-panel">
      <header className="topbar"><div><Icon name="chat" size={18} /><span>Ask your documents</span><span className="header-divider">/</span><span className="muted">{messages.length ? 'Conversation' : 'New conversation'}</span></div><span className="context-badge"><Icon name="book" size={14} />Document-grounded answers</span></header>
      <section className={`conversation ${messages.length ? 'has-messages' : ''}`} aria-label="Conversation">
        {!messages.length ? <div className="welcome">
          <div className="welcome-symbol"><Icon name="sparkle" size={32} /><span className="small-spark">✦</span></div>
          <div className="eyebrow">LESS SEARCHING. MORE UNDERSTANDING.</div>
          <h1>Your documents.<br /><span>A world of answers.</span></h1>
          <p className="welcome-description">Turn information into insight. Upload your documents,<br className="desktop-break" /> ask a question, and let your knowledge do the talking.</p>
          <div className="steps"><span><b>1</b>Upload a PDF</span><i /><span><b>2</b>Ask anything</span><i /><span><b>3</b>Explore the sources</span></div>
        </div> : <div className="message-list">{messages.map((message, index) => <article className={`chat-message ${message.role}`} key={index}><span className={`message-avatar ${message.role}`} >{message.role === 'user' ? 'Y' : <Icon name="sparkle" size={18} />}</span><div className="message-body"><div className="message-label">{message.role === 'user' ? 'You' : 'Raglab'}{message.role === 'assistant' && !message.error && <span>DOCUMENT ASSISTANT</span>}</div><div className={`answer-text ${message.role === 'assistant' && !message.error ? 'markdown-content' : ''} ${message.error ? 'error' : ''}`}>{message.role === 'assistant' && !message.error ? <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown> : message.content}</div>{!!message.sources?.length && <div className="sources"><div className="sources-label"><Icon name="book" size={15} />Sources · {message.sources.length}</div>{message.sources.map((source, sourceIndex) => <details key={sourceIndex}><summary><span className="source-number">{sourceIndex + 1}</span><span>{source.filename ?? 'Document'}</span>{source.page !== null && <small>Page {source.page}</small>}<Icon name="chevron" size={14} /></summary><p>{source.content}</p></details>)}</div>}</div></article>)}{isLoading && <div className="thinking" role="status"><Icon name="sparkle" size={18} /><span>Looking through your documents</span><span className="loading-dots">•••</span></div>}<div ref={messagesEndRef} /></div>}
      </section>
      <div className="composer-area"><form className="composer" onSubmit={event => { event.preventDefault(); void askQuestion(); }}><label htmlFor="question" className="visually-hidden">Ask a question about your documents</label><textarea ref={queryInput} id="question" rows={2} value={query} placeholder="What would you like to know about your documents?" disabled={isLoading} onChange={event => setQuery(event.target.value)} onKeyDown={event => { if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); void askQuestion(); } }} /><div className="composer-bottom"><span><Icon name="book" size={15} />Your knowledge base</span><div><small>Enter to send</small><button type="submit" aria-label="Send question" disabled={isLoading || !query.trim()}><Icon name="arrow" size={19} /></button></div></div></form><p className="composer-note">Answers are based on retrieved context. Always check the sources.</p></div>
    </main>
  </div>;
}
export default App;
