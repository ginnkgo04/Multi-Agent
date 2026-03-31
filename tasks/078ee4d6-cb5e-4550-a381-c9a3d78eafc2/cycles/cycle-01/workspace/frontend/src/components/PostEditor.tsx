'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createThread, createPost, uploadImage } from '@/lib/api';
import { useAuth } from '@/lib/auth';

interface PostEditorProps {
  mode: 'thread' | 'reply';
  categoryId?: string;
  threadId?: string;
  onSuccess?: () => void;
  onCancel?: () => void;
  placeholder?: string;
  initialContent?: string;
  initialTitle?: string;
}

export default function PostEditor({
  mode,
  categoryId,
  threadId,
  onSuccess,
  onCancel,
  placeholder = 'Share your thoughts...',
  initialContent = '',
  initialTitle = ''
}: PostEditorProps) {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [title, setTitle] = useState(initialTitle);
  const [content, setContent] = useState(initialContent);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadingImage, setUploadingImage] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [content]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isAuthenticated) {
      setError('Please log in to post');
      router.push('/auth/login');
      return;
    }

    if (mode === 'thread' && !title.trim()) {
      setError('Title is required');
      return;
    }

    if (!content.trim()) {
      setError('Content is required');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      if (mode === 'thread' && categoryId) {
        const thread = await createThread({
          title: title.trim(),
          content: content.trim(),
          category_id: categoryId
        });
        onSuccess?.();
        router.push(`/forum/${categoryId}/${thread.id}`);
      } else if (mode === 'reply' && threadId) {
        const post = await createPost({
          content: content.trim(),
          thread_id: threadId
        });
        onSuccess?.();
        setContent('');
        setTitle('');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to submit. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please upload an image file');
      return;
    }

    // Validate file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      setError('Image size must be less than 5MB');
      return;
    }

    setUploadingImage(true);
    setError(null);

    try {
      const imageUrl = await uploadImage(file);
      const cursorPos = textareaRef.current?.selectionStart || content.length;
      const newContent = content.slice(0, cursorPos) + `\n![image](${imageUrl})\n` + content.slice(cursorPos);
      setContent(newContent);
    } catch (err: any) {
      setError(err.message || 'Failed to upload image');
    } finally {
      setUploadingImage(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleSubmit(e);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
        <p className="text-gray-600 mb-4">You need to be logged in to post</p>
        <button
          onClick={() => router.push('/auth/login')}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Log In
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
            <span className="text-blue-600 font-semibold">
              {user?.username?.[0]?.toUpperCase() || 'U'}
            </span>
          </div>
          <div>
            <p className="font-medium text-gray-900">{user?.username || 'User'}</p>
            <p className="text-sm text-gray-500">
              {mode === 'thread' ? 'Creating new thread' : 'Replying to thread'}
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="p-4">
        {mode === 'thread' && (
          <div className="mb-4">
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Thread title"
              className="w-full px-4 py-3 text-lg font-semibold border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isSubmitting}
            />
          </div>
        )}

        <div className="mb-4">
          <textarea
            ref={textareaRef}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none min-h-[120px]"
            disabled={isSubmitting}
            rows={4}
          />
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}

        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={isSubmitting || uploadingImage}
              className="px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploadingImage ? 'Uploading...' : 'Upload Image'}
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
              disabled={isSubmitting || uploadingImage}
            />
            <button
              type="button"
              onClick={() => setContent(content + ' **bold**')}
              disabled={isSubmitting}
              className="px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50"
            >
              Bold
            </button>
            <button
              type="button"
              onClick={() => setContent(content + ' *italic*')}
              disabled={isSubmitting}
              className="px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50"
            >
              Italic
            </button>
            <button
              type="button"
              onClick={() => setContent(content + ' `code`')}
              disabled={isSubmitting}
              className="px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50"
            >
              Code
            </button>
          </div>

          <div className="flex items-center space-x-3">
            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                disabled={isSubmitting}
                className="px-4 py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
            )}
            <button
              type="submit"
              disabled={isSubmitting || !content.trim() || (mode === 'thread' && !title.trim())}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Posting...</span>
                </>
              ) : (
                <span>{mode === 'thread' ? 'Create Thread' : 'Post Reply'}</span>
              )}
            </button>
          </div>
        </div>

        <div className="mt-4 text-xs text-gray-