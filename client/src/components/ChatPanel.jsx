import React, { useState, useEffect, useRef } from 'react';
import { Button, Input, List, Avatar, App, Spin } from 'antd';
import { SendOutlined, ClearOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons';
import api from '../utils/api';
import { renderMarkdown } from '../utils/markdown';

const ChatPanel = ({ videoId }) => {
  const { message } = App.useApp();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [fetchingHistory, setFetchingHistory] = useState(false);
  const scrollRef = useRef(null);

  const suggestionChips = [
    "Summarize the main takeaways",
    "List the key decisions made",
    "What action items were assigned?",
    "Were there any open questions?"
  ];

  useEffect(() => {
    fetchHistory();
  }, [videoId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchHistory = async () => {
    setFetchingHistory(true);
    try {
      const response = await api.get(`/api/chat/history/${videoId}`);
      setMessages(response.data.messages || []);
    } catch (err) {
      console.error(err);
      message.error("Failed to load chat history");
    } finally {
      setFetchingHistory(false);
    }
  };

  const handleSend = async (text) => {
    const queryText = text || inputValue;
    if (!queryText.trim()) return;

    // Clear main input if used
    if (!text) setInputValue('');

    const newMsg = { role: 'user', content: queryText, timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, newMsg]);
    setLoading(true);

    try {
      const response = await api.post(`/api/chat/query/${videoId}`, {
        question: queryText
      });
      const assistantMsg = {
        role: 'assistant',
        content: response.data.answer,
        timestamp: new Date().toISOString()
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error(err);
      message.error(err.response?.data?.detail || "Failed to get response");
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    try {
      await api.delete(`/api/chat/clear/${videoId}`);
      setMessages([]);
      message.success("Chat history cleared");
    } catch (err) {
      console.error(err);
      message.error("Failed to clear chat history");
    }
  };

  const scrollToBottom = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900/40 rounded-xl border border-white/5 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-white/5 flex items-center justify-between bg-white/2">
        <div className="flex items-center gap-2">
          <RobotOutlined className="text-violet-400 text-lg" />
          <span className="font-semibold text-white">Interactive Assistant</span>
        </div>
        {messages.length > 0 && (
          <Button 
            type="text" 
            danger 
            icon={<ClearOutlined />} 
            onClick={handleClearHistory}
            className="hover:bg-red-500/10"
          >
            Clear
          </Button>
        )}
      </div>

      {/* Messages */}
      <div 
        ref={scrollRef}
        className="flex-1 p-4 overflow-y-auto space-y-4"
      >
        {fetchingHistory ? (
          <div className="h-full flex items-center justify-center">
            <Spin size="large" />
          </div>
        ) : messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-gray-500">
            <RobotOutlined className="text-4xl text-gray-600 mb-2" />
            <p className="font-medium text-gray-400">Ask any question about this video</p>
            <p className="text-xs text-gray-500 mt-1 max-w-[240px]">
              Type a prompt or choose from the options below to query the video knowledge base.
            </p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div 
              key={index}
              className={`flex items-start gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <Avatar 
                icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />} 
                className={msg.role === 'user' ? 'bg-violet-600' : 'bg-slate-700'} 
              />
              <div 
                className={`max-w-[75%] p-3 rounded-2xl text-sm leading-relaxed ${
                  msg.role === 'user' 
                    ? 'bg-violet-600 text-white rounded-tr-none' 
                    : 'bg-white/5 text-gray-200 border border-white/5 rounded-tl-none'
                }`}
              >
                {msg.role === 'user' ? msg.content : renderMarkdown(msg.content)}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex items-start gap-3">
            <Avatar icon={<RobotOutlined />} className="bg-slate-700" />
            <div className="p-3 bg-white/5 border border-white/5 rounded-2xl rounded-tl-none">
              <Spin size="small" />
            </div>
          </div>
        )}
      </div>

      {/* Suggestions and Input */}
      <div className="p-4 border-t border-white/5 bg-white/2 space-y-3">
        {messages.length === 0 && (
          <div className="flex flex-wrap gap-1.5">
            {suggestionChips.map((chip, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(chip)}
                disabled={loading}
                className="text-xs px-2.5 py-1.5 rounded-lg bg-white/5 hover:bg-violet-600/20 hover:text-violet-400 border border-white/5 hover:border-violet-500/30 text-gray-400 cursor-pointer transition-all disabled:opacity-50"
              >
                {chip}
              </button>
            ))}
          </div>
        )}
        <div className="flex gap-2">
          <Input 
            placeholder="Type your question..." 
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onPressEnter={() => handleSend()}
            disabled={loading}
            className="bg-white/5 border-white/10 hover:border-violet-500 focus:border-violet-500 text-white rounded-lg h-10 flex-1"
          />
          <Button 
            type="primary" 
            icon={<SendOutlined />} 
            onClick={() => handleSend()}
            disabled={loading || !inputValue.trim()}
            className="bg-violet-600 hover:bg-violet-500 border-0 h-10 rounded-lg"
          />
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;
