'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { X, Sparkles, ArrowLeft } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useStudioStore, getTotalCharCount, getAllSourceMaterial, canGenerate } from '@/stores/studio/useStudioStore';
import { useEditorStore } from '@/stores/editor/useEditorStore';
import { studioProcessorsApi, studioPackagesApi } from '@/lib/api/studio';
import { studioGenerationService } from '@/lib/services/studioGenerationService';
import { InputView, GeneratingView, ResultView } from '@/components/studio/views';
import type { ProcessorWithConfig, UploadedSource, LessonOutline } from '@/types/studio';

export default function StudioPage() {
  const router = useRouter();

  // Store state
  const {
    currentView,
    setCurrentView,
    sources,
    setSources,
    courseTitle,
    setCourseTitle,
    selectedProcessorId,
    setSelectedProcessorId,
    sourceInfo,
    setSourceInfo,
    streamedContent,
    streamStatus,
    generatedPackage,
    setGeneratedPackage,
    selectedLessonId,
    setSelectedLessonId,
    resetGeneration,
    reset,
    // Generation state from store
    isGenerating,
    isPaused,
    generationPhase,
    currentLessonIndex,
    totalLessons,
    lessonsOutline,
    completedLessons,
    completedLessonsData,
    generationError,
    currentProcessor,
    setCurrentProcessor,
  } = useStudioStore();

  // Local state
  const [processors, setProcessors] = useState<ProcessorWithConfig[]>([]);
  const [showPasteInput, setShowPasteInput] = useState(false);
  const [pastedText, setPastedText] = useState('');
  const [previewSource, setPreviewSource] = useState<UploadedSource | null>(null);
  const [copiedJson, setCopiedJson] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const streamContainerRef = useRef<HTMLDivElement>(null);

  // Load processors
  useEffect(() => {
    const loadProcessors = async () => {
      try {
        const result = await studioProcessorsApi.list();
        setProcessors(result.processors);
      } catch (error) {
        console.error('Failed to load processors:', error);
      }
    };
    loadProcessors();
  }, []);

  // Auto-scroll streaming content
  useEffect(() => {
    if (streamContainerRef.current) {
      streamContainerRef.current.scrollTop = streamContainerRef.current.scrollHeight;
    }
  }, [streamedContent]);

  // Auto-navigate to editor when generation completes
  useEffect(() => {
    if (currentView === 'result' && generatedPackage) {
      // Load the generated package into the editor store
      useEditorStore.getState().loadFromPackage(generatedPackage);
      // Reset studio state before navigation
      studioGenerationService.cancel();
      reset();
      // Navigate to the editor
      router.push('/admin/editor/new');
    }
  }, [currentView, generatedPackage, router, reset]);

  // Handle add pasted text
  const handleAddPastedText = () => {
    if (!pastedText.trim()) return;
    const newSource: UploadedSource = {
      id: `paste-${Date.now()}`,
      name: `粘贴文本 ${sources.length + 1}`,
      charCount: pastedText.length,
      text: pastedText,
      type: 'paste',
    };
    setSources([...sources, newSource]);
    setPastedText('');
    setShowPasteInput(false);
  };

  // Get current processor from list
  const activeProcessor = processors.find(p => p.id === selectedProcessorId) || currentProcessor || null;

  // Check if can generate
  const canStartGenerate = () => canGenerate(sources, courseTitle);

  // Handle generate - use service
  const handleGenerate = useCallback(() => {
    if (!canStartGenerate()) return;
    const processor = processors.find(p => p.id === selectedProcessorId) || null;
    studioGenerationService.startGeneration(processor);
  }, [courseTitle, sources, sourceInfo, selectedProcessorId, processors]);

  // Handle cancel
  const handleCancelGenerate = () => {
    studioGenerationService.cancel();
    resetGeneration();
  };

  // Handle retry - only available when there's an error
  const handleRetry = useCallback(() => {
    const processor = processors.find(p => p.id === selectedProcessorId) || null;
    studioGenerationService.retry(processor);
  }, [processors, selectedProcessorId]);

  // Handle pause
  const handlePause = useCallback(() => {
    studioGenerationService.pause();
  }, []);

  // Handle resume
  const handleResume = useCallback(() => {
    studioGenerationService.resume();
  }, []);

  // Handle copy JSON
  const handleCopyJson = async () => {
    if (!generatedPackage) return;
    await navigator.clipboard.writeText(JSON.stringify(generatedPackage, null, 2));
    setCopiedJson(true);
    setTimeout(() => setCopiedJson(false), 2000);
  };

  // Handle export JSON
  const handleExportJson = () => {
    if (!generatedPackage) return;
    const blob = new Blob([JSON.stringify(generatedPackage, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${generatedPackage.meta.title || 'course'}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Handle reset
  const handleReset = () => {
    studioGenerationService.cancel();
    resetGeneration();
  };

  // Handle save to database
  const handleSaveToDatabase = async () => {
    if (!generatedPackage || isSaving) return;

    setIsSaving(true);
    try {
      const result = await studioPackagesApi.saveToDatabase(generatedPackage);
      if (result.success) {
        alert(`课程已保存成功！课程 ID: ${result.course_id}`);
        // Reset studio state after successful save
        studioGenerationService.cancel();
        reset();
      }
    } catch (error) {
      console.error('Failed to save to database:', error);
      alert('保存失败，请重试');
    } finally {
      setIsSaving(false);
    }
  };

  // Handle enter editor - load package into editor and navigate
  const handleEnterEditor = useCallback(() => {
    if (!generatedPackage) return;

    // Load the generated package into the editor store
    useEditorStore.getState().loadFromPackage(generatedPackage);

    // Reset studio state before navigation
    studioGenerationService.cancel();
    reset();

    // Navigate to the editor with 'new' as courseId
    router.push('/admin/editor/new');
  }, [generatedPackage, router, reset]);

  // Get selected lesson
  const selectedLesson = generatedPackage?.lessons.find(l => l.lesson_id === selectedLessonId) || null;

  return (
    <div className="min-h-[calc(100vh-180px)] flex flex-col -mx-6 -my-8">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-slate-200 bg-white flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-red-100 rounded-xl flex items-center justify-center">
            <Sparkles size={20} className="text-red-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">HERCU Studio</h1>
            <p className="text-sm text-slate-500">AI 课程生成工具</p>
          </div>
        </div>
        {currentView !== 'input' && (
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-4 py-2 text-sm text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <ArrowLeft size={16} />
            返回
          </button>
        )}
      </div>

      {/* Content */}
      {currentView === 'input' && (
        <InputView
          sources={sources}
          setSources={setSources}
          showPasteInput={showPasteInput}
          setShowPasteInput={setShowPasteInput}
          pastedText={pastedText}
          setPastedText={setPastedText}
          handleAddPastedText={handleAddPastedText}
          setPreviewSource={setPreviewSource}
          courseTitle={courseTitle}
          setCourseTitle={setCourseTitle}
          sourceInfo={sourceInfo}
          setSourceInfo={setSourceInfo}
          processors={processors}
          selectedProcessorId={selectedProcessorId}
          setSelectedProcessorId={setSelectedProcessorId}
          canGenerate={canStartGenerate}
          handleGenerate={handleGenerate}
        />
      )}

      {currentView === 'generating' && (
        <GeneratingView
          generationPhase={generationPhase}
          currentLessonIndex={currentLessonIndex}
          totalLessons={totalLessons}
          lessonsOutline={lessonsOutline}
          completedLessons={completedLessons}
          completedLessonsData={completedLessonsData}
          currentProcessor={activeProcessor}
          streamStatus={streamStatus}
          streamedContent={streamedContent}
          streamContainerRef={streamContainerRef}
          courseTitle={courseTitle}
          sources={sources}
          handleCancelGenerate={handleCancelGenerate}
          generationError={generationError}
          handleRetry={handleRetry}
          isPaused={isPaused}
          handlePause={handlePause}
          handleResume={handleResume}
        />
      )}

      {currentView === 'result' && generatedPackage && (
        <ResultView
          generatedPackage={generatedPackage}
          selectedLessonId={selectedLessonId}
          setSelectedLessonId={setSelectedLessonId}
          selectedLesson={selectedLesson}
          copiedJson={copiedJson}
          handleCopyJson={handleCopyJson}
          handleExportJson={handleExportJson}
          handleReset={handleReset}
          handleEnterEditor={handleEnterEditor}
          handleSaveToDatabase={handleSaveToDatabase}
          isSaving={isSaving}
        />
      )}

      {/* Preview Modal */}
      {previewSource && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-8">
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[80vh] flex flex-col">
            <div className="p-4 border-b border-slate-200 flex items-center justify-between">
              <h3 className="font-bold text-slate-900">{previewSource.name}</h3>
              <button
                onClick={() => setPreviewSource(null)}
                className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
              >
                <X size={20} className="text-slate-500" />
              </button>
            </div>
            <div className="flex-1 overflow-auto p-4">
              <pre className="whitespace-pre-wrap text-sm text-slate-700">{previewSource.text}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
