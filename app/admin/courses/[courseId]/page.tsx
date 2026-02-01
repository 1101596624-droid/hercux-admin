'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  getCourseDetail,
  deleteCourse,
  publishCourse,
  type CourseDetail
} from '@/lib/api/admin/courses';

export default function CourseDetailPage() {
  const router = useRouter();
  const params = useParams();
  const courseId = parseInt(params.courseId as string);

  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [loading, setLoading] = useState(true);

  // Load course detail
  useEffect(() => {
    loadCourse();
  }, [courseId]);

  const loadCourse = async () => {
    setLoading(true);
    try {
      const data = await getCourseDetail(courseId);
      setCourse(data);
    } catch (error) {
      console.error('Failed to load course:', error);
      alert('加载课程失败');
      router.push('/admin/courses');
    } finally {
      setLoading(false);
    }
  };

  // Handle delete
  const handleDelete = async () => {
    if (!course) return;

    if (!confirm(`确定要删除课程 "${course.name}" 吗？此操作不可撤销。`)) {
      return;
    }

    try {
      await deleteCourse(courseId);
      alert('课程已删除');
      router.push('/admin/courses');
    } catch (error) {
      console.error('Failed to delete course:', error);
      alert('删除失败，请重试');
    }
  };

  // Handle publish toggle
  const handlePublishToggle = async () => {
    if (!course) return;

    try {
      await publishCourse(courseId, !course.is_published);
      loadCourse();
    } catch (error) {
      console.error('Failed to toggle publish status:', error);
      alert('操作失败，请重试');
    }
  };

  // Difficulty badge color
  const getDifficultyColor = (difficulty: string) => {
    const colors = {
      beginner: 'bg-green-100 text-green-800',
      intermediate: 'bg-blue-100 text-blue-800',
      advanced: 'bg-orange-100 text-orange-800',
      expert: 'bg-red-100 text-red-800'
    };
    return colors[difficulty as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  // Difficulty label
  const getDifficultyLabel = (difficulty: string) => {
    const labels = {
      beginner: '初级',
      intermediate: '中级',
      advanced: '高级',
      expert: '专家'
    };
    return labels[difficulty as keyof typeof labels] || difficulty;
  };

  // Node type label
  const getNodeTypeLabel = (type: string) => {
    const labels = {
      lesson: '课程',
      quiz: '测验',
      exercise: '练习',
      project: '项目',
      assessment: '评估'
    };
    return labels[type as keyof typeof labels] || type;
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
            onClick={() => router.push('/admin/courses')}
            className="text-slate-600 hover:text-slate-900"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-slate-900">{course.name}</h1>
            <p className="mt-2 text-slate-600">{course.description || '暂无描述'}</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handlePublishToggle}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                course.is_published
                  ? 'bg-green-100 text-green-800 hover:bg-green-200'
                  : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
              }`}
            >
              {course.is_published ? '已发布' : '未发布'}
            </button>
            <button
              onClick={() => router.push(`/admin/courses/${courseId}/edit`)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              编辑
            </button>
            <button
              onClick={handleDelete}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              删除
            </button>
          </div>
        </div>
      </div>

      {/* Course Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">难度</p>
          <div className="mt-2">
            <span className={`px-3 py-1 text-sm font-medium rounded-full ${getDifficultyColor(course.difficulty)}`}>
              {getDifficultyLabel(course.difficulty)}
            </span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">讲师</p>
          <p className="mt-2 text-lg font-semibold text-slate-900">{course.instructor || '-'}</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">时长</p>
          <p className="mt-2 text-lg font-semibold text-slate-900">
            {course.duration_hours ? `${course.duration_hours} 小时` : '-'}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">创建时间</p>
          <p className="mt-2 text-lg font-semibold text-slate-900">
            {new Date(course.created_at).toLocaleDateString('zh-CN')}
          </p>
        </div>
      </div>

      {/* Tags */}
      {course.tags && course.tags.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200 mb-8">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">标签</h2>
          <div className="flex flex-wrap gap-2">
            {course.tags.map((tag, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">总节点数</p>
          <p className="mt-2 text-3xl font-bold text-slate-900">{course.statistics.total_nodes}</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">学员数</p>
          <p className="mt-2 text-3xl font-bold text-blue-600">{course.statistics.enrolled_users}</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">完成率</p>
          <p className="mt-2 text-3xl font-bold text-green-600">
            {course.statistics.completion_rate.toFixed(1)}%
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">近30天注册</p>
          <p className="mt-2 text-3xl font-bold text-purple-600">{course.statistics.recent_enrollments}</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">总完成数</p>
          <p className="mt-2 text-3xl font-bold text-orange-600">{course.statistics.total_completions}</p>
        </div>
      </div>

      {/* Course Nodes */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">课程节点</h2>
          <button
            onClick={() => router.push(`/admin/courses/${courseId}/nodes`)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            管理节点
          </button>
        </div>

        {course.nodes.length === 0 ? (
          <div className="p-12 text-center text-slate-600">
            <p>暂无课程节点</p>
            <button
              onClick={() => router.push(`/admin/courses/${courseId}/nodes`)}
              className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
            >
              添加第一个节点
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    序号
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    节点ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    标题
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    类型
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    父节点
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {course.nodes.map((node) => (
                  <tr key={node.id} className="hover:bg-slate-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                      {node.sequence}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-slate-600">
                      {node.node_id}
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-900">
                      {node.title}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {getNodeTypeLabel(node.type)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {node.parent_id || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
