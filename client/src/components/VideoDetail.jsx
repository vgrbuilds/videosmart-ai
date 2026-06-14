import React, { useState, useEffect } from 'react';
import { Button, Tabs, Card, Spin, Table, Tag, Input, Result } from 'antd';
import { ArrowLeftOutlined, SearchOutlined, SoundOutlined, CalendarOutlined, TrophyOutlined } from '@ant-design/icons';
import api from '../utils/api';
import ChatPanel from './ChatPanel';
import { renderMarkdown } from '../utils/markdown';

const VideoDetail = ({ videoId, onBack }) => {
  const [video, setVideo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchVideoDetails();
  }, [videoId]);

  const fetchVideoDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/api/videos/${videoId}`);
      setVideo(response.data);
    } catch (err) {
      console.error(err);
      setError("Failed to load video insights. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-glow-grid">
        <Spin size="large" description="Analyzing video transcript and gathering insights..." />
      </div>
    );
  }

  if (error || !video) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Result
          status="error"
          title="Failed to Load"
          subTitle={error || "Video not found"}
          extra={[
            <Button type="primary" key="back" onClick={onBack} className="bg-violet-600 border-0">
              Back to Dashboard
            </Button>
          ]}
        />
      </div>
    );
  }

  // Highlight matches in the transcript text
  const getHighlightedText = (text, highlight) => {
    if (!text) return '';
    if (!highlight.trim()) return text;
    const parts = text.split(new RegExp(`(${highlight})`, 'gi'));
    return (
      <span>
        {parts.map((part, i) => 
          part.toLowerCase() === highlight.toLowerCase() 
            ? <mark key={i} className="bg-yellow-500/30 text-yellow-200 px-0.5 rounded">{part}</mark> 
            : part
        )}
      </span>
    );
  };



  const tabItems = [
    {
      key: 'summary',
      label: 'Summary',
      children: (
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-2 text-violet-400">
            <SoundOutlined />
            <h3 className="text-lg font-bold text-white m-0">Meeting Summary</h3>
          </div>
          <div className="text-gray-300 text-sm leading-relaxed p-5 bg-white/2 rounded-xl border border-white/5">
            {renderMarkdown(video.summary) || "Summary generation in progress."}
          </div>
        </div>
      )
    },
    {
      key: 'decisions',
      label: 'Key Decisions',
      children: (
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-2 text-emerald-400">
            <TrophyOutlined />
            <h3 className="text-lg font-bold text-white m-0">Decisions Made</h3>
          </div>
          {renderMarkdown(video.key_decisions) || <p className="text-gray-400 italic">None generated.</p>}
        </div>
      )
    },
    {
      key: 'action_items',
      label: 'Action Items',
      children: (
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-2 text-blue-400">
            <CalendarOutlined />
            <h3 className="text-lg font-bold text-white m-0">Assigned Tasks</h3>
          </div>
          {renderMarkdown(video.action_items) || <p className="text-gray-400 italic">None generated.</p>}
        </div>
      )
    },
    {
      key: 'questions',
      label: 'Open Questions',
      children: (
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-2 text-amber-400">
            <SearchOutlined />
            <h3 className="text-lg font-bold text-white m-0">Questions & Follow-ups</h3>
          </div>
          {renderMarkdown(video.open_questions) || <p className="text-gray-400 italic">None generated.</p>}
        </div>
      )
    },
    {
      key: 'transcript',
      label: 'Transcript',
      children: (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-2">
            <h3 className="text-lg font-bold text-white m-0">Full Transcript</h3>
            <Input
              placeholder="Search transcript..."
              prefix={<SearchOutlined className="text-gray-400" />}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-white/5 border-white/10 hover:border-violet-500 focus:border-violet-500 text-white rounded-lg w-full sm:w-64 h-9"
            />
          </div>
          <div className="text-gray-300 text-sm leading-relaxed max-h-[50vh] overflow-y-auto p-5 bg-white/2 rounded-xl border border-white/5 whitespace-pre-line">
            {video.transcript ? getHighlightedText(video.transcript, searchTerm) : "Transcript not available."}
          </div>
        </div>
      )
    }
  ];

  return (
    <div className="min-h-screen relative overflow-hidden flex flex-col">
      {/* Background Grid & Glows */}
      <div className="bg-glow-grid" />
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-violet-600/5 rounded-full blur-3xl" />
      
      {/* Header Panel */}
      <div className="p-4 sm:p-6 border-b border-white/5 bg-slate-950/40 relative z-10 glass-panel">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row sm:items-center gap-4 justify-between">
          <div className="flex items-center gap-4">
            <Button 
              icon={<ArrowLeftOutlined />} 
              onClick={onBack}
              className="bg-white/5 border-white/10 hover:border-violet-500 hover:text-violet-400 text-white rounded-lg h-10 w-10 flex items-center justify-center flex-shrink-0"
            />
            <div>
              <h1 className="text-xl sm:text-2xl font-extrabold tracking-tight text-white m-0">
                {video.title || "Processed Video"}
              </h1>
              <div className="flex items-center gap-2 mt-1">

                <Tag color="green" className="border-0 font-semibold text-xs py-0.5 px-2">
                  Completed
                </Tag>
                <span className="text-gray-500 text-xs">
                  Processed on {new Date(video.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
          {video.url && (
            <a 
              href={video.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center px-4 h-10 rounded-lg bg-violet-600/20 hover:bg-violet-600/30 text-violet-300 hover:text-violet-200 border border-violet-500/20 font-semibold text-sm transition-all"
            >
              Watch Video
            </a>
          )}
        </div>
      </div>

      {/* Main Grid View */}
      <div className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 grid grid-cols-1 lg:grid-cols-3 gap-6 relative z-10">
        {/* Left: Insights & Details Tabs */}
        <div className="lg:col-span-2 flex flex-col">
          <Card className="glass-card flex-1 border-0 shadow-lg" styles={{ body: { padding: '1.5rem', display: 'flex', flexDirection: 'column', height: '100%' } }}>
            <Tabs 
              defaultActiveKey="summary" 
              items={tabItems}
              className="detail-tabs flex-1 flex flex-col"
            />
          </Card>
        </div>

        {/* Right: RAG Chat Assistant */}
        <div className="lg:col-span-1 h-[75vh] lg:h-auto">
          <ChatPanel videoId={videoId} />
        </div>
      </div>
    </div>
  );
};

export default VideoDetail;
