import React, { useState, useEffect, useRef } from 'react';
import { Card, Button, Input, Select, Upload, Tabs, Tag, Spin, Popconfirm, App } from 'antd';
import { 
  InboxOutlined, 
  YoutubeOutlined, 
  PlayCircleOutlined, 
  DeleteOutlined, 
  LoadingOutlined, 
  VideoCameraOutlined,
  LogoutOutlined,
  UserOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import api from '../utils/api';

const { Dragger } = Upload;


const Dashboard = ({ user, onLogout, onViewVideo }) => {
  const { message } = App.useApp();
  const [videos, setVideos] = useState([]);
  const [loadingList, setLoadingList] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  // Form States
  const [activeTab, setActiveTab] = useState('file');
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [fileList, setFileList] = useState([]);
  
  const pollingRef = useRef(null);

  useEffect(() => {
    fetchVideos();
    return () => stopPolling();
  }, []);

  useEffect(() => {
    // Check if any video is still processing
    const hasProcessing = videos.some(v => v.status === 'processing');
    if (hasProcessing) {
      startPolling();
    } else {
      stopPolling();
    }
  }, [videos]);

  const fetchVideos = async (silent = false) => {
    if (!silent) setLoadingList(true);
    try {
      const response = await api.get('/api/videos/');
      setVideos(response.data || []);
    } catch (err) {
      console.error(err);
      message.error("Failed to load video list");
    } finally {
      if (!silent) setLoadingList(false);
    }
  };

  const startPolling = () => {
    if (pollingRef.current) return;
    pollingRef.current = setInterval(() => {
      fetchVideos(true);
    }, 5000);
  };

  const stopPolling = () => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  };

  const handleUpload = async () => {
    if (activeTab === 'file' && fileList.length === 0) {
      message.warning("Please select a video file to upload!");
      return;
    }
    if (activeTab === 'youtube' && !youtubeUrl.trim()) {
      message.warning("Please input a valid YouTube URL!");
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('language', 'english');

    if (activeTab === 'file') {
      formData.append('file', fileList[0]);
    } else {
      formData.append('youtube_url', youtubeUrl);
    }

    try {
      await api.post('/api/videos/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });
      
      message.success("Video upload accepted. Processing started in the background!");
      setYoutubeUrl('');
      setFileList([]);
      fetchVideos();
    } catch (err) {
      console.error(err);
      const errMsg = err.response?.data?.detail || "Failed to process video";
      message.error(errMsg);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/api/videos/${id}`);
      message.success("Video deleted successfully");
      fetchVideos();
    } catch (err) {
      console.error(err);
      message.error("Failed to delete video");
    }
  };

  const draggerProps = {
    onRemove: (file) => {
      setFileList([]);
    },
    beforeUpload: (file) => {
      setFileList([file]);
      return false; // Prevent auto-upload
    },
    fileList,
    maxCount: 1,
  };

  return (
    <div className="min-h-screen relative overflow-hidden flex flex-col">
      {/* Background Grid & Glows */}
      <div className="bg-glow-grid" />
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-violet-600/5 rounded-full blur-3xl" />
      <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-blue-600/5 rounded-full blur-3xl" />

      {/* Header Banner */}
      <header className="p-4 sm:p-6 border-b border-white/5 bg-slate-950/40 relative z-10 glass-panel">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/20">
              <VideoCameraOutlined className="text-white text-xl" />
            </div>
            <div>
              <h1 className="text-xl font-extrabold tracking-tight text-white m-0">VideoSmart AI</h1>
              <p className="text-gray-500 text-xs mt-0.5">Meeting Insights and Transcription</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 text-gray-300 bg-white/5 px-3 py-1.5 rounded-lg border border-white/5">
              <UserOutlined className="text-violet-400" />
              <span className="text-xs font-semibold">{user?.username || user?.email}</span>
            </div>
            <Button 
              icon={<LogoutOutlined />} 
              onClick={onLogout}
              className="bg-white/5 border-white/10 hover:border-red-500 hover:text-red-500 text-white rounded-lg h-9"
            >
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 space-y-8 relative z-10">
        
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card className="glass-card border-0 shadow-lg h-full" styles={{ body: { padding: '1.5rem', display: 'flex', flexDirection: 'column', height: '100%' } }}>
              <div className="flex items-center justify-between mb-4 border-b border-white/5 pb-2">
                <h2 className="text-base font-bold text-white m-0">Analyze New Video</h2>
              </div>

              <Tabs 
                activeKey={activeTab} 
                onChange={setActiveTab}
                className="upload-tabs flex-1 flex flex-col"
                items={[
                  {
                    key: 'file',
                    label: 'Local File Upload',
                    children: (
                      <div className="py-4">
                        <Dragger {...draggerProps} className="bg-white/2 hover:bg-white/4 border-dashed border-white/10 hover:border-violet-500/50 rounded-xl p-8 transition-colors">
                          <p className="ant-upload-drag-icon text-violet-400 text-4xl mb-2">
                            <InboxOutlined />
                          </p>
                          <p className="text-gray-300 font-semibold text-sm">Click or drag video/audio file here</p>
                          <p className="text-gray-500 text-xs mt-1">Supports MP4, MP3, WAV and other media formats</p>
                        </Dragger>
                      </div>
                    )
                  },
                  {
                    key: 'youtube',
                    label: 'YouTube Link',
                    children: (
                      <div className="py-8 space-y-4">
                        <div className="space-y-2">
                          <label className="text-xs text-gray-400 font-semibold uppercase tracking-wider">YouTube URL</label>
                          <Input 
                            placeholder="https://www.youtube.com/watch?v=..." 
                            prefix={<YoutubeOutlined className="text-red-500" />}
                            value={youtubeUrl}
                            onChange={(e) => setYoutubeUrl(e.target.value)}
                            className="bg-white/5 border-white/10 hover:border-violet-500 focus:border-violet-500 text-white rounded-lg h-11"
                          />
                        </div>
                      </div>
                    )
                  }
                ]}
              />

              <div className="mt-4 pt-4 border-t border-white/5 flex items-center justify-between">
                {uploading ? (
                  <div className="flex items-center gap-3 text-violet-400 text-sm">
                    <Spin indicator={<LoadingOutlined style={{ fontSize: 18 }} spin />} />
                    <span>Uploading... {uploadProgress}%</span>
                  </div>
                ) : <div />}
                <Button
                  type="primary"
                  onClick={handleUpload}
                  loading={uploading}
                  className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 border-0 h-10 px-6 font-semibold shadow-lg shadow-violet-500/25 rounded-lg"
                >
                  Process Video
                </Button>
              </div>
            </Card>
          </div>

          <div className="lg:col-span-1">
            <Card className="glass-card border-0 shadow-lg h-full" styles={{ body: { padding: '1.5rem' } }}>
              <h2 className="text-base font-bold text-white mb-3">Quick Statistics</h2>
              <div className="grid grid-cols-2 gap-4 mt-2">
                <div className="bg-white/2 p-4 rounded-xl border border-white/5">
                  <div className="text-gray-400 text-xs font-semibold">Total Analyzed</div>
                  <div className="text-white text-3xl font-extrabold mt-1">{videos.length}</div>
                </div>
                <div className="bg-white/2 p-4 rounded-xl border border-white/5">
                  <div className="text-gray-400 text-xs font-semibold">Completed</div>
                  <div className="text-emerald-400 text-3xl font-extrabold mt-1">
                    {videos.filter(v => v.status === 'completed').length}
                  </div>
                </div>
              </div>
              <div className="mt-6 bg-violet-600/10 border border-violet-500/20 p-4 rounded-xl">
                <h3 className="text-sm font-bold text-violet-300 m-0">Background Processing</h3>
                <p className="text-gray-400 text-xs mt-1.5 leading-relaxed">
                  We process transcriptions, summarization, and key insight extraction in background threads. You can safely close or navigate away; the interface will update once processing completes.
                </p>
              </div>
            </Card>
          </div>
        </section>

        {/* Video directory */}
        <section className="space-y-4">
          <div className="flex items-center justify-between border-b border-white/5 pb-2">
            <h2 className="text-lg font-extrabold text-white tracking-tight m-0">Library Directory</h2>
            {videos.some(v => v.status === 'processing') && (
              <span className="text-xs text-violet-400 flex items-center gap-1.5 font-medium animate-pulse">
                <Spin indicator={<LoadingOutlined style={{ fontSize: 12 }} spin />} />
                Auto-updating dashboard...
              </span>
            )}
          </div>

          {loadingList ? (
            <div className="py-20 flex items-center justify-center">
              <Spin size="large" description="Loading library database..." />
            </div>
          ) : videos.length === 0 ? (
            <div className="py-16 text-center glass-card rounded-2xl border-0">
              <VideoCameraOutlined className="text-5xl text-gray-700 mb-2" />
              <p className="text-gray-400 font-semibold">No video sessions found</p>
              <p className="text-xs text-gray-500 mt-1 max-w-sm mx-auto">
                Upload your first audio/video file or input a YouTube link to generate transcripts and run AI RAG queries.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {videos.map((vid) => (
                <Card 
                  key={vid.id}
                  className="glass-card border-0 hover:border-violet-500/20 hover:scale-[1.01] transition-all duration-300"
                  styles={{ body: { padding: '1.25rem', display: 'flex', flexDirection: 'column', height: '100%', minHeight: '210px' } }}
                >
                  <div className="flex-1 space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="text-sm font-bold text-white leading-snug line-clamp-2 m-0" title={vid.title}>
                        {vid.title || (vid.status === 'processing' ? 'Processing File...' : 'Upload Session')}
                      </h3>
                    </div>

                    <p className="text-xs text-gray-400 line-clamp-3 leading-relaxed">
                      {vid.summary || (vid.status === 'processing' ? 'Running audio diagnostics, transcription algorithms, and summarizing key takeaways...' : vid.status === 'failed' ? `Error: ${vid.error_message}` : 'No summary generated')}
                    </p>
                  </div>

                  <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between">
                    <div>
                      {vid.status === 'completed' && (
                        <Tag color="green" className="border-0 text-[10px] font-semibold">Ready</Tag>
                      )}
                      {vid.status === 'processing' && (
                        <Tag color="gold" className="border-0 text-[10px] font-semibold animate-pulse flex items-center gap-1">
                          <Spin indicator={<LoadingOutlined style={{ fontSize: 9 }} spin />} />
                          Processing
                        </Tag>
                      )}
                      {vid.status === 'failed' && (
                        <Popconfirm 
                          title="Failure Cause" 
                          description={vid.error_message || "Unknown error"} 
                          icon={<ExclamationCircleOutlined className="text-red-500" />}
                          okText="Close" 
                          showCancel={false}
                        >
                          <Tag color="red" className="border-0 text-[10px] font-semibold cursor-pointer">
                            Failed
                          </Tag>
                        </Popconfirm>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      {vid.status === 'completed' && (
                        <Button 
                          type="primary" 
                          icon={<PlayCircleOutlined />}
                          onClick={() => onViewVideo(vid.id)}
                          className="bg-violet-600 hover:bg-violet-500 border-0 h-8 rounded-lg text-xs font-semibold"
                        >
                          View Insights
                        </Button>
                      )}
                      <Popconfirm
                        title="Delete video insights?"
                        description="This deletes transcripts, summaries, action items, and vectors."
                        onConfirm={() => handleDelete(vid.id)}
                        okText="Yes, Delete"
                        cancelText="Cancel"
                        okButtonProps={{ danger: true }}
                      >
                        <Button 
                          type="text" 
                          danger
                          icon={<DeleteOutlined />}
                          className="hover:bg-red-500/10 h-8 w-8 rounded-lg flex items-center justify-center"
                        />
                      </Popconfirm>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
};

export default Dashboard;
