/**
 * VideoStep - 视频步骤组件
 * 支持视频播放和待制作占位符显示
 */

import { Video, Clock, FileText, AlertCircle } from 'lucide-react';

interface VideoStepProps {
  video_spec: {
    video_id?: string;
    duration?: string;
    video_url?: string;
    status?: 'pending' | 'ready' | 'hidden';
    placeholder?: boolean;
    production_notes?: string;
    script?: {
      scenes?: Array<{
        timecode: string;
        scene?: string;
        narration: string;
      }>;
    };
  };
}

export function VideoStep({ video_spec }: VideoStepProps) {
  const isPending = video_spec?.status === 'pending' || video_spec?.placeholder || !video_spec?.video_url;
  const scenesCount = video_spec?.script?.scenes?.length || 0;

  // 待制作状态 - 显示占位符
  if (isPending) {
    return (
      <div className="space-y-4">
        {/* 视频占位符 */}
        <div className="bg-gradient-to-br from-slate-100 to-slate-50 rounded-2xl p-8 border-2 border-dashed border-slate-300">
          <div className="text-center">
            {/* 视频图标 */}
            <div className="w-16 h-16 mx-auto mb-4 bg-slate-200 rounded-full flex items-center justify-center">
              <Video className="w-8 h-8 text-slate-400" />
            </div>

            {/* 状态文字 */}
            <p className="text-slate-600 font-medium text-lg mb-1">视频内容待制作</p>
            <p className="text-sm text-slate-500">视频资源正在准备中</p>

            {/* 时长信息 */}
            {video_spec?.duration && (
              <div className="mt-4 inline-flex items-center gap-2 px-3 py-1.5 bg-white rounded-full border border-slate-200">
                <Clock className="w-4 h-4 text-slate-400" />
                <span className="text-sm text-slate-600">预计时长: {video_spec.duration}</span>
              </div>
            )}

            {/* 脚本状态 */}
            {scenesCount > 0 && (
              <div className="mt-3 inline-flex items-center gap-2 px-3 py-1.5 bg-green-50 rounded-full border border-green-200">
                <FileText className="w-4 h-4 text-green-500" />
                <span className="text-sm text-green-700">{scenesCount} 个场景脚本已准备</span>
              </div>
            )}
          </div>
        </div>

        {/* 脚本预览 */}
        {video_spec?.script?.scenes && video_spec.script.scenes.length > 0 && (
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="px-4 py-3 bg-slate-50 border-b border-slate-200">
              <p className="text-sm font-medium text-slate-700 flex items-center gap-2">
                <FileText className="w-4 h-4" />
                视频脚本预览
              </p>
            </div>
            <div className="divide-y divide-slate-100">
              {video_spec.script.scenes.slice(0, 4).map((scene, i) => (
                <div key={i} className="px-4 py-3 hover:bg-slate-50 transition-colors">
                  <div className="flex items-start gap-3">
                    <span className="flex-shrink-0 px-2 py-0.5 bg-purple-100 text-purple-700 text-xs font-mono rounded">
                      {scene.timecode}
                    </span>
                    <div className="flex-1 min-w-0">
                      {scene.scene && (
                        <p className="text-xs text-slate-500 mb-1">[{scene.scene}]</p>
                      )}
                      <p className="text-sm text-slate-700 line-clamp-2">{scene.narration}</p>
                    </div>
                  </div>
                </div>
              ))}
              {video_spec.script.scenes.length > 4 && (
                <div className="px-4 py-2 text-center text-xs text-slate-500 bg-slate-50">
                  还有 {video_spec.script.scenes.length - 4} 个场景...
                </div>
              )}
            </div>
          </div>
        )}

        {/* 制作说明 */}
        {video_spec?.production_notes && (
          <div className="bg-amber-50 rounded-xl p-4 border border-amber-200">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-amber-800 mb-1">制作说明</p>
                <p className="text-sm text-amber-700">{video_spec.production_notes}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // 正常视频播放
  return (
    <div className="space-y-4">
      {/* 视频播放器 */}
      <div className="bg-black rounded-xl overflow-hidden aspect-video">
        {video_spec.video_url ? (
          <video
            src={video_spec.video_url}
            controls
            className="w-full h-full"
            poster="/images/video-poster.jpg"
          >
            您的浏览器不支持视频播放
          </video>
        ) : (
          <div className="w-full h-full flex items-center justify-center text-white">
            <Video className="w-12 h-12 opacity-50" />
          </div>
        )}
      </div>

      {/* 视频信息 */}
      {video_spec.duration && (
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Clock className="w-4 h-4" />
          <span>时长: {video_spec.duration}</span>
        </div>
      )}
    </div>
  );
}
