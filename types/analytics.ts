// 数据分析相关类型定义

// 时间范围
export type TimeRange = '24h' | '7d' | '30d' | '90d' | '1y' | 'custom';

export interface CustomTimeRange {
  startDate: string;
  endDate: string;
}

// 统计概览
export interface DashboardStats {
  totalUsers: number;
  activeUsers: number; // last 30 days
  newUsers: number; // last 30 days
  userGrowthRate: number; // percentage

  totalCourses: number;
  publishedCourses: number;
  draftCourses: number;

  totalEnrollments: number;
  activeEnrollments: number;
  completedEnrollments: number;

  totalLearningHours: number;
  averageLearningHours: number;

  systemHealth: 'healthy' | 'degraded' | 'down';
}

// 用户分析
export interface UserAnalytics {
  registrationTrend: TrendData[];
  activeUsersTrend: TrendData[];
  retentionRate: RetentionData[];
  usersByRole: DistributionData[];
  usersBySubscription: DistributionData[];
  topUsers: TopUserData[];
  userEngagement: EngagementData;
}

export interface TrendData {
  date: string;
  value: number;
  label?: string;
}

export interface RetentionData {
  cohort: string; // e.g., "2024-01"
  day1: number;
  day7: number;
  day14: number;
  day30: number;
  day60: number;
  day90: number;
}

export interface DistributionData {
  name: string;
  value: number;
  percentage: number;
  color?: string;
}

export interface TopUserData {
  userId: string;
  userName: string;
  userAvatar?: string;
  metric: number;
  metricLabel: string;
  rank: number;
}

export interface EngagementData {
  dailyActiveUsers: number;
  weeklyActiveUsers: number;
  monthlyActiveUsers: number;
  averageSessionDuration: number; // minutes
  averageSessionsPerUser: number;
  bounceRate: number; // percentage
}

// 课程分析
export interface CourseAnalytics {
  enrollmentTrend: TrendData[];
  completionTrend: TrendData[];
  topCourses: TopCourseData[];
  coursesByCategory: DistributionData[];
  coursesByDifficulty: DistributionData[];
  averageCompletionRate: number;
  averageRating: number;
  coursePerformance: CoursePerformanceData[];
}

export interface TopCourseData {
  courseId: string;
  courseTitle: string;
  courseThumbnail?: string;
  enrollments: number;
  completions: number;
  completionRate: number;
  averageRating: number;
  revenue?: number;
  rank: number;
}

export interface CoursePerformanceData {
  courseId: string;
  courseTitle: string;
  enrollments: number;
  activeStudents: number;
  completions: number;
  completionRate: number;
  averageScore: number;
  averageRating: number;
  dropoffRate: number;
  averageCompletionTime: number; // hours
}

// 学习分析
export interface LearningAnalytics {
  learningHoursTrend: TrendData[];
  completionRateTrend: TrendData[];
  averageScoreTrend: TrendData[];
  learningHeatmap: HeatmapData[];
  nodeCompletionFunnel: FunnelData[];
  strugglingTopics: StrugglingTopicData[];
}

export interface HeatmapData {
  day: string; // 'Monday', 'Tuesday', etc.
  hour: number; // 0-23
  value: number; // activity count
}

export interface FunnelData {
  stage: string;
  value: number;
  percentage: number;
  dropoff: number;
}

export interface StrugglingTopicData {
  topicId: string;
  topicName: string;
  courseId: string;
  courseName: string;
  attempts: number;
  averageScore: number;
  completionRate: number;
  averageTime: number; // minutes
  strugglingUsers: number;
}

// 系统分析
export interface SystemAnalytics {
  apiCallsTrend: TrendData[];
  errorRateTrend: TrendData[];
  responseTimeTrend: TrendData[];
  storageUsageTrend: TrendData[];
  bandwidthUsageTrend: TrendData[];
  topEndpoints: EndpointData[];
  errorBreakdown: DistributionData[];
}

export interface EndpointData {
  endpoint: string;
  method: string;
  calls: number;
  averageResponseTime: number; // ms
  errorRate: number; // percentage
  p95ResponseTime: number; // ms
  p99ResponseTime: number; // ms
}

// 报表
export interface Report {
  id: string;
  name: string;
  description: string;
  type: 'user' | 'course' | 'learning' | 'system' | 'custom';
  schedule?: ReportSchedule;
  format: 'pdf' | 'excel' | 'csv';
  recipients: string[];
  createdBy: string;
  createdAt: string;
  lastGenerated?: string;
}

export interface ReportSchedule {
  frequency: 'daily' | 'weekly' | 'monthly';
  dayOfWeek?: number; // 0-6 for weekly
  dayOfMonth?: number; // 1-31 for monthly
  time: string; // HH:mm
  timezone: string;
}

export interface ReportData {
  reportId: string;
  generatedAt: string;
  timeRange: {
    start: string;
    end: string;
  };
  summary: Record<string, any>;
  charts: ChartData[];
  tables: TableData[];
}

export interface ChartData {
  id: string;
  title: string;
  type: 'line' | 'bar' | 'pie' | 'area' | 'scatter';
  data: any[];
  config?: Record<string, any>;
}

export interface TableData {
  id: string;
  title: string;
  columns: TableColumn[];
  rows: any[];
}

export interface TableColumn {
  key: string;
  label: string;
  type?: 'text' | 'number' | 'date' | 'currency' | 'percentage';
  sortable?: boolean;
  width?: number;
}

// 实时数据
export interface RealtimeMetrics {
  currentActiveUsers: number;
  currentApiCalls: number; // per minute
  currentErrorRate: number; // percentage
  currentResponseTime: number; // ms
  recentActivities: RecentActivity[];
  timestamp: string;
}

export interface RecentActivity {
  id: string;
  type: string;
  description: string;
  userId?: string;
  userName?: string;
  timestamp: string;
}

// 对比分析
export interface ComparisonData {
  current: {
    period: string;
    value: number;
  };
  previous: {
    period: string;
    value: number;
  };
  change: number; // absolute change
  changePercentage: number;
  trend: 'up' | 'down' | 'stable';
}
