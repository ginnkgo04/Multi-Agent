'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createPost, updatePost } from '@/lib/api';
import { getCurrentUser } from '@/lib/auth';

interface PostEditorProps {
  threadId?: string;
  postId?: string;
  initialContent?: string;
  onSuccess?: () => void;
  onCancel?: () => void;
  isReply?: boolean;
  parentPostId?: string;
  mode?: 'create' | 'edit';
}

export default function PostEditor({
  threadId,
  postId,
  initialContent = '',
  onSuccess,
  onCancel,
  isReply = false,
  parentPostId,
  mode = 'create'
}: PostEditorProps) {
  const [content, setContent] = useState(initialContent);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewMode, setPreviewMode] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const router = useRouter();

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [content]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!content.trim()) {
      setError('Content cannot be empty');
      return;
    }

    const user = getCurrentUser();
    if (!user) {
      setError('You must be logged in to post');
      router.push('/auth/login');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      if (mode === 'edit' && postId) {
        await updatePost(postId, { content });
      } else {
        if (!threadId) {
          throw new Error('Thread ID is required for new posts');
        }
        
        await createPost({
          content,
          thread_id: threadId,
          parent_post_id: parentPostId
        });
      }

      setContent('');
      if (onSuccess) {
        onSuccess();
      } else if (threadId) {
        router.refresh();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save post');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFormat = (format: 'bold' | 'italic' | 'code' | 'quote' | 'link') => {
    if (!textareaRef.current) return;

    const textarea = textareaRef.current;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = content.substring(start, end);
    let formattedText = '';

    switch (format) {
      case 'bold':
        formattedText = `**${selectedText}**`;
        break;
      case 'italic':
        formattedText = `*${selectedText}*`;
        break;
      case 'code':
        formattedText = `\`${selectedText}\``;
        break;
      case 'quote':
        formattedText = `> ${selectedText}`;
        break;
      case 'link':
        formattedText = `[${selectedText}](url)`;
        break;
    }

    const newContent = content.substring(0, start) + formattedText + content.substring(end);
    setContent(newContent);

    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + formattedText.length, start + formattedText.length);
    }, 0);
  };

  const renderPreview = () => {
    const renderMarkdown = (text: string) => {
      return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded">$1</code>')
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="text-blue-600 hover:underline">$1</a>')
        .replace(/^> (.*)$/gm, '<blockquote class="border-l-4 border-gray-300 pl-4 italic">$1</blockquote>')
        .replace(/\n/g, '<br>');
    };

    return (
      <div 
        className="prose max-w-none p-4 bg-white rounded-lg border border-gray-300 min-h-[200px]"
        dangerouslySetInnerHTML={{ __html: renderMarkdown(content) || '<p class="text-gray-400">Preview will appear here...</p>' }}
      />
    );
  };

  return (
    <div className="w-full bg-white rounded-lg shadow-md p-4 md:p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          {mode === 'edit' ? 'Edit Post' : isReply ? 'Write a Reply' : 'Create a New Post'}
        </h3>
        <div className="flex space-x-2">
          <button
            type="button"
            onClick={() => setPreviewMode(!previewMode)}
            className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
          >
            {previewMode ? 'Edit' : 'Preview'}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {!previewMode ? (
          <>
            <div className="mb-4 flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => handleFormat('bold')}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
                title="Bold"
              >
                <strong>B</strong>
              </button>
              <button
                type="button"
                onClick={() => handleFormat('italic')}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
                title="Italic"
              >
                <em>I</em>
              </button>
              <button
                type="button"
                onClick={() => handleFormat('code')}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
                title="Code"
              >
                <code>{'</>'}</code>
              </button>
              <button
                type="button"
                onClick={() => handleFormat('quote')}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
                title="Quote"
              >
                "
              </button>
              <button
                type="button"
                onClick={() => handleFormat('link')}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
                title="Link"
              >
                🔗
              </button>
            </div>

            <textarea
              ref={textareaRef}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={isReply ? "Write your reply here..." : "Write your post here..."}
              className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[200px] resize-none transition-colors"
              disabled={isSubmitting}
            />

            <div className="mt-2 text-sm text-gray-500">
              Supports basic Markdown: **bold**, *italic*, `code`, &gt; quote, [link](url)
            </div>
          </>
        ) : (
          <div className="mb-4">
            {renderPreview()}
          </div>
        )}

        <div className="flex flex-col sm:flex-row justify-between items-center mt-6 space-y-3 sm:space-y-0">
          <div className="text-sm text-gray-500">
            {content.length} characters
          </div>
          
          <div className="flex space-x-3">
            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                disabled={isSubmitting}
              >
                Cancel
              </button>
            )}
            
            <button
              type="submit"
              disabled={isSubmitting || !content.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isSubmitting ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.