'use client';

import { useState, useEffect } from 'react';
import { Message, User } from '@/types/api';

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [newUser, setNewUser] = useState({ username: '', email: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const API_BASE_URL = 'http://localhost:8000';

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [messagesRes, usersRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/messages`),
        fetch(`${API_BASE_URL}/api/users`)
      ]);

      if (messagesRes.ok && usersRes.ok) {
        const messagesData = await messagesRes.json();
        const usersData = await usersRes.json();
        setMessages(messagesData.messages || []);
        setUsers(usersData.users || []);
      } else {
        setError('Failed to fetch data from API');
      }
    } catch (err) {
      setError('Error connecting to backend API');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: newMessage,
          sender: 'User',
          timestamp: new Date().toISOString(),
        }),
      });

      if (response.ok) {
        setNewMessage('');
        fetchData();
      }
    } catch (err) {
      setError('Failed to send message');
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUser.username.trim() || !newUser.email.trim()) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newUser),
      });

      if (response.ok) {
        setNewUser({ username: '', email: '' });
        fetchData();
      }
    } catch (err) {
      setError('Failed to create user');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            AIxMultimodal
          </h1>
          <p className="text-gray-600">
            Full-stack application with Next.js and FastAPI
          </p>
          {error && (
            <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Messages Section */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Messages
            </h2>
            
            {/* Message Form */}
            <form onSubmit={handleSendMessage} className="mb-6">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Type a message..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Send
                </button>
              </div>
            </form>

            {/* Messages List */}
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {messages.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No messages yet</p>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className="p-3 bg-gray-50 rounded-lg border-l-4 border-blue-500"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium text-gray-800">
                          {message.sender}
                        </p>
                        <p className="text-gray-600">{message.content}</p>
                      </div>
                      <span className="text-xs text-gray-400">
                        {message.timestamp
                          ? new Date(message.timestamp).toLocaleTimeString()
                          : ''}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Users Section */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Users
            </h2>
            
            {/* User Form */}
            <form onSubmit={handleCreateUser} className="mb-6">
              <div className="space-y-3">
                <input
                  type="text"
                  value={newUser.username}
                  onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                  placeholder="Username"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <input
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                  placeholder="Email"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  type="submit"
                  className="w-full px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  Add User
                </button>
              </div>
            </form>

            {/* Users List */}
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {users.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No users yet</p>
              ) : (
                users.map((user) => (
                  <div
                    key={user.id}
                    className="p-3 bg-gray-50 rounded-lg border-l-4 border-green-500"
                  >
                    <p className="font-medium text-gray-800">{user.username}</p>
                    <p className="text-sm text-gray-600">{user.email}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* API Status */}
        <div className="mt-8 text-center">
          <div className="inline-flex items-center px-4 py-2 bg-gray-100 rounded-full">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            <span className="text-sm text-gray-600">
              Backend API: {error ? 'Disconnected' : 'Connected'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
