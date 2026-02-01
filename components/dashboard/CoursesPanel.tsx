'use client';

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui';
import { Button } from '@/components/ui';
import { Progress } from '@/components/ui';
import { Badge } from '@/components/ui';
import Link from 'next/link';
import type { Course } from '@/types/course';

interface CoursesPanelProps {
  courses: Course[];
  maxDisplay?: number;
}

export function CoursesPanel({ courses, maxDisplay = 6 }: CoursesPanelProps) {
  const displayedCourses = courses.slice(0, maxDisplay);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>我的课程</CardTitle>
          <Link href="/courses">
            <Button variant="ghost" size="sm">
              查看全部 →
            </Button>
          </Link>
        </div>
      </CardHeader>
      <CardContent>
        {displayedCourses.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-3">📚</div>
            <p className="text-dark-500 mb-4">还没有正在学习的课程</p>
            <Link href="/courses">
              <Button>浏览课程</Button>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {displayedCourses.map((course) => (
              <Link
                key={course.id}
                href={course.enrolled ? `/courses/${course.id}/learn` : `/courses`}
              >
                <Card
                  variant="outlined"
                  hoverable
                  className="h-full transition-all cursor-pointer"
                >
                  <CardContent className="p-4 flex flex-col h-full">
                    <div className="mb-3">
                      <Badge variant="primary" size="sm" className="mb-2">
                        {course.category}
                      </Badge>
                      <h4 className="font-semibold text-dark-900 mb-1 line-clamp-2">
                        {course.title}
                      </h4>
                      <p className="text-xs text-dark-500 line-clamp-2">
                        {course.subtitle}
                      </p>
                    </div>

                    <div className="mt-auto space-y-3">
                      {course.progress !== undefined && course.progress > 0 && (
                        <div>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs text-dark-600">进度</span>
                            <span className="text-xs font-semibold text-dark-900">
                              {course.progress}%
                            </span>
                          </div>
                          <Progress value={course.progress} size="sm" />
                        </div>
                      )}

                      <div className="flex items-center justify-between text-xs text-dark-500">
                        <div className="flex items-center gap-3">
                          <span>📊 {course.nodes} 节点</span>
                          <span>⏱️ {Math.floor(course.duration / 60)}h</span>
                        </div>
                        <Badge
                          variant="default"
                          size="sm"
                          className="text-xs"
                        >
                          {course.difficulty}
                        </Badge>
                      </div>

                      <div className="flex items-center gap-2 pt-2 border-t border-dark-100">
                        <img
                          src={course.instructor.avatar}
                          alt={course.instructor.name}
                          className="w-6 h-6 rounded-full"
                          onError={(e) => {
                            e.currentTarget.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(course.instructor.name)}&background=DC2626&color=fff`;
                          }}
                        />
                        <span className="text-xs text-dark-600">
                          {course.instructor.name}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
