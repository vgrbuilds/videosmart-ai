import React, { useState } from 'react';
import { Card, Form, Input, Button, Tabs, App } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, SafetyCertificateOutlined } from '@ant-design/icons';
import api from '../utils/api';

const Auth = ({ onAuthSuccess }) => {
  const { message } = App.useApp();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('login');

  const onFinish = async (values) => {
    setLoading(true);
    try {
      if (activeTab === 'login') {
        const response = await api.post('/api/auth/login', {
          email: values.email,
          password: values.password,
        });
        const { access_token } = response.data;
        localStorage.setItem('token', access_token);
        
        // Fetch user profile info
        const profileRes = await api.get('/api/auth/profile');
        localStorage.setItem('user', JSON.stringify(profileRes.data));
        
        message.success('Welcome back!');
        onAuthSuccess(profileRes.data, access_token);
      } else {
        await api.post('/api/auth/register', {
          username: values.username,
          email: values.email,
          password: values.password,
        });
        message.success('Registration successful! Please login.');
        setActiveTab('login');
      }
    } catch (err) {
      console.error(err);
      const errMsg = err.response?.data?.detail || 'An error occurred. Please try again.';
      message.error(errMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden px-4">
      {/* Background Grids & Glow */}
      <div className="bg-glow-grid" />
      
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl" />

      <Card 
        className="w-full max-w-md glass-panel shadow-2xl relative z-10 border-0"
        styles={{ body: { padding: '2.5rem' } }}
      >
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-violet-600 to-indigo-600 mb-4 shadow-lg shadow-violet-500/25">
            <SafetyCertificateOutlined className="text-white text-2xl" />
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-white m-0">VideoSmart AI</h1>
          <p className="text-gray-400 text-sm mt-1">Video Intelligence and Conversational RAG</p>
        </div>

        <Tabs 
          activeKey={activeTab} 
          onChange={setActiveTab} 
          centered 
          className="auth-tabs mb-6"
          items={[
            { label: 'Sign In', key: 'login' },
            { label: 'Register', key: 'register' }
          ]}
        />

        <Form
          name="auth_form"
          layout="vertical"
          onFinish={onFinish}
          requiredMark={false}
        >
          {activeTab === 'login' ? (
            <Form.Item
              name="email"
              rules={[
                { required: true, message: 'Please input your Email!' },
                { type: 'email', message: 'Please enter a valid email!' }
              ]}
            >
              <Input 
                prefix={<UserOutlined className="text-gray-400" />} 
                placeholder="Email Address" 
                size="large"
                className="bg-white/5 border-white/10 hover:border-violet-500 focus:border-violet-500 text-white rounded-lg h-11"
              />
            </Form.Item>
          ) : (
            <>
              <Form.Item
                name="username"
                rules={[
                  { required: true, message: 'Please input your Username!' },
                  { min: 3, message: 'Username must be at least 3 characters!' }
                ]}
              >
                <Input 
                  prefix={<UserOutlined className="text-gray-400" />} 
                  placeholder="Username" 
                  size="large"
                  className="bg-white/5 border-white/10 hover:border-violet-500 focus:border-violet-500 text-white rounded-lg h-11"
                />
              </Form.Item>
              <Form.Item
                name="email"
                rules={[
                  { required: true, message: 'Please input your Email!' },
                  { type: 'email', message: 'Please enter a valid email!' }
                ]}
              >
                <Input 
                  prefix={<MailOutlined className="text-gray-400" />} 
                  placeholder="Email Address" 
                  size="large"
                  className="bg-white/5 border-white/10 hover:border-violet-500 focus:border-violet-500 text-white rounded-lg h-11"
                />
              </Form.Item>
            </>
          )}

          <Form.Item
            name="password"
            rules={[
              { required: true, message: 'Please input your Password!' },
              { min: 6, message: 'Password must be at least 6 characters!' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined className="text-gray-400" />}
              placeholder="Password"
              size="large"
              className="bg-white/5 border-white/10 hover:border-violet-500 focus:border-violet-500 text-white rounded-lg h-11"
            />
          </Form.Item>

          <Form.Item className="mt-8 mb-0">
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
              block
              size="large"
              className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 border-0 h-11 text-base font-semibold shadow-lg shadow-violet-500/25 rounded-lg"
            >
              {activeTab === 'login' ? 'Sign In' : 'Create Account'}
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Auth;
