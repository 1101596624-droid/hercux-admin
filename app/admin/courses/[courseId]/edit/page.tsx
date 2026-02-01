'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  getCourseDetail,
  updateCourse,
  type CourseDetail,
  type CourseFormData
} from '@/lib/api/admin/courses';

export default function CourseEditPage() {
  const router = useRouter();
  const params = useParams();
  const courseId = parseInt(params.courseId as string);

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [course, setCourse] = useState<CourseDetail | null>(null);

  // Form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [difficulty, setDifficulty] = useState<'beginner' | 'intermediate' | 'advanced' | 'expert'>('beginner');
  const [instructor, setInstructor] = useState('');
  const [durationHours, setDurationHours] = useState<number | ''>('');
  const [thumbnailUrl, setThumbnailUrl] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');

  // Load course
  useEffect(() => {
    loadCourse();
  }, [courseId]);

  const loadCourse = async () => {
    setLoading(true);
    try {
      const data = await getCourseDetail(courseId);
      setCourse(data);

      // Populate form
      setName(data.name);
      setDescription(data.description || '');
      setDifficulty(data.difficulty as any);
      setInstructor(data.instructor || '');
      setDurationHours(data.duration_hours || '');
      setThumbnailUrl(data.thumbnail_url || '');
      setTags(data.tags || []);
    } catch (error) {
      console.error('Failed to load course:', error);
      alert('加载课程失败');
      router.push('/admin/courses');
    } finally {
      setLoading(false);
    }
  };

  // Handle tag add
  const handleAddTag = () => {
    const trimmedTag = tagInput.trim();
    if (trimmedTag && !tags.includes(trimmedTag)) {
      setTags([...tags, trimmedTag]);
      setTagInput('');
    }
  };

  // Handle tag remove
  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  // Handle submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      alert('请输入课程名称');
      return;
    }

    setSubmitting(true);
    try {
      const formData: Partial<CourseFormData> = {
        name: name.trim(),
        description: description.trim() || undefined,
        difficulty,
        instructor: instructor.trim() || undefined,
        duration_hours: durationHours ? Number(durationHours) : undefined,
        thumbnail_url: thumbnailUrl.trim() || undefined,
        tags: tags.length > 0 ? tags : undefined
      };

      await updateCourse(courseId, formData);
      alert('课程更新成功');
      router.push(`/admin/courses/${courseId}`);
    } catch (error) {
      console.error('Failed to update course:', error);
      alert('更新失败，请重试');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-slate-600">加载中...</div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-slate-600">课程未找到</div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <button
            onClick={() => router.push(`/admin/courses/${courseId}`)}
            className="text-slate-600 hover:text-slate-900"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div>
            <h1 className="text-3xl font-bold text-slate-900">编辑课程</h1>
            <p className="mt-2 text-slate-600">修改课程信息</p>
          </div>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="max-w-4xl">
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 space-y-6">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              课程名称 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="输入课程名称"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              课程描述
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="输入课程描述"
            />
          </div>

          {/* Difficulty */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              难度 <span className="text-red-500">*</span>
            </label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value as any)}
              required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="beginner">初级</option>
              <option value="intermediate">中级</option>
              <option value="advanced">高级</option>
              <option value="expert">专家</option>
            </select>
          </div>

          {/* Instructor */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              讲师
            </label>
            <input
              type="text"
              value={instructor}
              onChange={(e) => setInstructor(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="输入讲师名称"
            />
          </div>

          {/* Duration */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              时长（小时）
            </label>
            <input
              type="number"
              value={durationHours}
              onChange={(e) => setDurationHours(e.target.value ? Number(e.target.value) : '')}
              min="0"
              step="0.5"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="输入课程时长"
            />
          </div>

          {/* Thumbnail URL */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              缩略图URL
            </label>
            <input
              type="url"
              value={thumbnailUrl}
              onChange={(e) => setThumbnailUrl(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://example.com/image.jpg"
            />
            {thumbnailUrl && (
              <div className="mt-2">
                <img
                  src={thumbnailUrl}
                  alt="缩略图预览"
                  className="w-32 h-32 object-cover rounded-lg border border-slate-200"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                  }}
                />
              </div>
            )}
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              标签
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddTag();
                  }
                }}
                className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="输入标签后按回车添加"
              />
              <button
                type="button"
                onClick={handleAddTag}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                添加
              </button>
            </div>
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {tags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full flex items-center gap-2"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => handleRemoveTag(tag)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="mt-6 flex gap-4">
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? '保存中...' : '保存更改'}
          </button>
          <button
            type="button"
            onClick={() => router.push(`/admin/courses/${courseId}`)}
            className="px-6 py-2 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 transition-colors"
          >
            取消
          </button>
        </div>
      </form>
    </div>
  );
}
