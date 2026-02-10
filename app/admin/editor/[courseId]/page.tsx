'use client';

/**
 * Course Editor Page
 * 课程编辑器页面 - 三段式布局
 */

import React, { useEffect, useState, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useEditorStore } from '@/stores/editor/useEditorStore';
import { courseEditorAPI } from '@/lib/api/admin/editor';
import { EditorLayout } from '@/components/editor/EditorLayout';
import { CourseStructurePanel } from '@/components/editor/left/CourseStructurePanel';
import { NodeConfigPanel } from '@/components/editor/center/NodeConfigPanel';
import { AIGuidancePanel } from '@/components/editor/right/AIGuidancePanel';
import { Button } from '@/components/ui/Button';
import { DIFFICULTY_LABELS, DIFFICULTY_COLORS, type CourseDifficulty } from '@/types/editor';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function CourseEditorPage() {
  const params = useParams();
  const router = useRouter();
  const courseId = params.courseId as string;
  const isNewCourse = courseId === 'new';

  const {
    loadCourse,
    courseTitle,
    setCourseTitle,
    courseCoverImage,
    setCourseCoverImage,
    courseDifficulty,
    setCourseDifficulty,
    courseTags,
    addCourseTag,
    removeCourseTag,
    isDirty,
    isSaving,
    setIsSaving,
    markClean,
    chapters,
    aiGuidance,
    reset,
    courseId: storeCourseId,
  } = useEditorStore();

  const [error, setError] = useState<string | null>(null);
  const [savedCourseId, setSavedCourseId] = useState<number | null>(null);
  const [importing, setImporting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const coverImageInputRef = useRef<HTMLInputElement>(null);
  const [uploadingCover, setUploadingCover] = useState(false);
  const [newTag, setNewTag] = useState('');

  // Local loading state to avoid store sync issues
  const [localLoading, setLocalLoading] = useState(!isNewCourse);

  // Load course data on mount (only for existing courses)
  useEffect(() => {
    // For new courses, initialize with empty course or load from store
    if (isNewCourse) {
      const currentChapters = useEditorStore.getState().chapters;
      const currentCourseId = useEditorStore.getState().courseId;

      if (!currentCourseId || currentChapters.length === 0) {
        // Initialize a new empty course
        loadCourse('new', {
          title: '新课程',
          coverImage: undefined,
          difficulty: 'intermediate',
          tags: [],
          chapters: [],
          aiGuidance: useEditorStore.getState().aiGuidance,
        });
      }
      setLocalLoading(false);
      return;
    }

    const fetchCourse = async () => {
      setLocalLoading(true);
      setError(null);
      try {
        console.log('Fetching course:', courseId);
        const data = await courseEditorAPI.getCourse(courseId);
        console.log('Course data received:', data);
        loadCourse(courseId, {
          title: data.title,
          coverImage: data.coverImage,
          difficulty: data.difficulty,
          tags: data.tags,
          chapters: data.chapters,
          aiGuidance: data.aiGuidance,
        });
        setLocalLoading(false);
      } catch (err) {
        console.error('Failed to load course:', err);
        setError(err instanceof Error ? err.message : '加载课程失败');
        setLocalLoading(false);
      }
    };

    fetchCourse();

    // Cleanup on unmount
    return () => {
      reset();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courseId, isNewCourse]);

  // Handle save (入库，下架状态)
  const handleSave = async () => {
    setIsSaving(true);
    try {
      if (isNewCourse && savedCourseId === null) {
        // Create new course in database (下架状态)
        const result = await courseEditorAPI.createCourse({
          title: courseTitle,
          coverImage: courseCoverImage,
          difficulty: courseDifficulty,
          tags: courseTags,
          chapters,
          aiGuidance,
        });
        setSavedCourseId(parseInt(result.courseId));
        markClean();
        alert('课程已入库（下架状态）');
      } else {
        // Update existing course
        const targetId = savedCourseId?.toString() || courseId;
        await courseEditorAPI.saveCourse(targetId, {
          title: courseTitle,
          coverImage: courseCoverImage,
          difficulty: courseDifficulty,
          tags: courseTags,
          chapters,
          aiGuidance,
        });
        markClean();
        alert('保存成功');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败');
    } finally {
      setIsSaving(false);
    }
  };

  // Handle publish (入库并上架)
  const handlePublish = async () => {
    setIsSaving(true);
    try {
      let targetCourseId: string;

      if (isNewCourse && savedCourseId === null) {
        // First create the course
        const result = await courseEditorAPI.createCourse({
          title: courseTitle,
          coverImage: courseCoverImage,
          difficulty: courseDifficulty,
          tags: courseTags,
          chapters,
          aiGuidance,
        });
        targetCourseId = result.courseId;
        setSavedCourseId(parseInt(targetCourseId));
      } else {
        // Save existing course first
        targetCourseId = savedCourseId?.toString() || courseId;
        await courseEditorAPI.saveCourse(targetCourseId, {
          title: courseTitle,
          coverImage: courseCoverImage,
          difficulty: courseDifficulty,
          tags: courseTags,
          chapters,
          aiGuidance,
        });
      }

      // Then publish
      await courseEditorAPI.publishCourse(targetCourseId);
      markClean();
      alert('课程已上架');
      // Redirect to courses list
      router.push('/admin/courses');
    } catch (err) {
      setError(err instanceof Error ? err.message : '上架失败');
    } finally {
      setIsSaving(false);
    }
  };

  // Handle import JSON file
  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.json')) {
      alert('只支持 JSON 文件');
      return;
    }

    setImporting(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${API_BASE_URL}/internal/import-package-file`, {
        method: 'POST',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || '导入失败');
      }

      const result = await response.json();
      alert(`导入成功！创建了 ${result.nodes_created} 个节点`);
      // Redirect to the imported course
      router.push(`/admin/editor/${result.course_id}`);
    } catch (error) {
      console.error('Failed to import course:', error);
      alert(error instanceof Error ? error.message : '导入失败，请重试');
    } finally {
      setImporting(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  // Handle cover image upload
  const handleCoverImageClick = () => {
    coverImageInputRef.current?.click();
  };

  const handleCoverImageChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('请选择图片文件');
      return;
    }

    // 限制文件大小为 5MB
    if (file.size > 5 * 1024 * 1024) {
      alert('图片大小不能超过 5MB');
      return;
    }

    setUploadingCover(true);
    try {
      // 将图片转换为 base64 或上传到服务器
      // 这里先使用 base64 作为临时方案
      const reader = new FileReader();
      reader.onload = (event) => {
        const base64 = event.target?.result as string;
        setCourseCoverImage(base64);
        setUploadingCover(false);
      };
      reader.onerror = () => {
        alert('读取图片失败');
        setUploadingCover(false);
      };
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('Failed to upload cover image:', error);
      alert('上传封面失败');
      setUploadingCover(false);
    } finally {
      if (coverImageInputRef.current) {
        coverImageInputRef.current.value = '';
      }
    }
  };

  const handleRemoveCoverImage = () => {
    setCourseCoverImage(null);
  };

  // Warn before leaving with unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [isDirty]);

  if (localLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-dark-50">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-dark-600">加载课程中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen flex items-center justify-center bg-dark-50">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 text-red-500">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <p className="text-dark-800 font-medium mb-2">加载失败</p>
          <p className="text-dark-500 text-sm mb-4">{error}</p>
          <Button onClick={() => router.back()}>返回</Button>
        </div>
      </div>
    );
  }

  const header = (
    <div className="flex items-center justify-between px-4 py-3 bg-white border-b border-dark-100">
      {/* Hidden file inputs */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".json"
        className="hidden"
      />
      <input
        type="file"
        ref={coverImageInputRef}
        onChange={handleCoverImageChange}
        accept="image/*"
        className="hidden"
      />

      <div className="flex items-center gap-4">
        <button
          onClick={() => router.back()}
          className="p-2 hover:bg-dark-100 rounded-lg transition-colors"
        >
          <svg className="w-5 h-5 text-dark-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </button>

        {/* 课程封面 */}
        <div className="relative group">
          {courseCoverImage ? (
            <div className="w-12 h-12 rounded-lg overflow-hidden border border-dark-200 relative">
              <img
                src={courseCoverImage}
                alt="课程封面"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-1">
                <button
                  onClick={handleCoverImageClick}
                  className="p-1 bg-white/20 rounded hover:bg-white/30"
                  title="更换封面"
                >
                  <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </button>
                <button
                  onClick={handleRemoveCoverImage}
                  className="p-1 bg-white/20 rounded hover:bg-red-500/50"
                  title="删除封面"
                >
                  <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={handleCoverImageClick}
              disabled={uploadingCover}
              className="w-12 h-12 rounded-lg border-2 border-dashed border-dark-300 hover:border-primary-400 flex items-center justify-center transition-colors"
              title="添加课程封面"
            >
              {uploadingCover ? (
                <div className="w-4 h-4 border-2 border-dark-300 border-t-primary-500 rounded-full animate-spin" />
              ) : (
                <svg className="w-5 h-5 text-dark-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              )}
            </button>
          )}
        </div>

        <div>
          <input
            type="text"
            value={courseTitle}
            onChange={(e) => setCourseTitle(e.target.value)}
            placeholder="课程标题"
            className="text-lg font-semibold text-dark-900 bg-transparent border-none focus:outline-none focus:ring-0 w-64"
          />
          <div className="flex items-center gap-2 text-xs text-dark-500">
            {isNewCourse && !savedCourseId ? (
              <span className="px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded">
                新课程 (未入库)
              </span>
            ) : (
              <span>ID: {savedCourseId || courseId}</span>
            )}
            {isDirty && (
              <span className="px-1.5 py-0.5 bg-amber-100 text-amber-700 rounded">
                未保存
              </span>
            )}
          </div>
        </div>

        {/* 难度选择器 */}
        <div className="flex items-center gap-1 ml-4">
          <span className="text-xs text-dark-500 mr-1">难度:</span>
          {(Object.keys(DIFFICULTY_LABELS) as CourseDifficulty[]).map((diff) => (
            <button
              key={diff}
              onClick={() => setCourseDifficulty(diff)}
              className={`
                px-2 py-1 rounded text-xs font-medium transition-all
                ${courseDifficulty === diff
                  ? DIFFICULTY_COLORS[diff]
                  : 'bg-dark-100 text-dark-500 hover:bg-dark-200'
                }
              `}
            >
              {DIFFICULTY_LABELS[diff]}
            </button>
          ))}
        </div>

        {/* 标签编辑器 */}
        <div className="flex items-center gap-2 ml-4">
          <span className="text-xs text-dark-500">标签:</span>
          <div className="flex items-center gap-1">
            {courseTags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 px-2 py-1 bg-slate-100 text-slate-700 text-xs rounded"
              >
                {tag}
                <button
                  onClick={() => removeCourseTag(tag)}
                  className="hover:text-red-500"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </span>
            ))}
            {courseTags.length < 3 && (
              <div className="flex items-center">
                <input
                  type="text"
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && newTag.trim()) {
                      addCourseTag(newTag.trim());
                      setNewTag('');
                    }
                  }}
                  placeholder="添加标签"
                  className="w-20 px-2 py-1 text-xs border border-dark-200 rounded focus:outline-none focus:border-primary-400"
                />
                <button
                  onClick={() => {
                    if (newTag.trim()) {
                      addCourseTag(newTag.trim());
                      setNewTag('');
                    }
                  }}
                  className="ml-1 p-1 text-dark-400 hover:text-primary-500"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </button>
              </div>
            )}
          </div>
          <span className="text-xs text-dark-400">({courseTags.length}/3)</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={handleImportClick}
          disabled={importing}
        >
          {importing ? (
            <span className="flex items-center gap-1">
              <span className="w-4 h-4 border-2 border-dark-300 border-t-dark-600 rounded-full animate-spin"></span>
              导入中...
            </span>
          ) : (
            <span className="flex items-center gap-1">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              导入课程
            </span>
          )}
        </Button>

        {/* 新课程（未入库）显示：入库 / 入库并上架 */}
        {isNewCourse && !savedCourseId ? (
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={handleSave}
              disabled={isSaving}
            >
              {isSaving ? '入库中...' : '入库（下架状态）'}
            </Button>
            <Button
              size="sm"
              onClick={handlePublish}
              disabled={isSaving}
            >
              入库并上架
            </Button>
          </>
        ) : (
          /* 已入库课程显示：保存 / 上架 */
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={handleSave}
              disabled={isSaving || !isDirty}
            >
              {isSaving ? '保存中...' : '保存'}
            </Button>
            <Button
              size="sm"
              onClick={handlePublish}
              disabled={isSaving}
            >
              保存并上架
            </Button>
          </>
        )}
      </div>
    </div>
  );

  return (
    <EditorLayout
      header={header}
      leftPanel={<CourseStructurePanel />}
      centerPanel={<NodeConfigPanel />}
      rightPanel={<AIGuidancePanel />}
    />
  );
}
