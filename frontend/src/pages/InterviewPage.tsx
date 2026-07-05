import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getInterviewSummary, startInterview, submitAnswer } from '@/api/interview';
import { getApiErrorMessage } from '@/api/client';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Spinner } from '@/components/ui/Spinner';
import { ErrorState } from '@/components/ui/ErrorState';
import { tr } from '@/i18n/tr';
import type {
  AnsweredQuestion,
  InterviewCategory,
  InterviewDifficulty,
  NextQuestion,
} from '@/types/interview';

/**
 * Backend TASKS.md kabul kriterine göre bir oturum 5 soru sonra biter
 * (API_CONTRACT.md bu sayıyı açıkça belirtmez; `is_session_complete` alanı
 * asıl doğruluk kaynağıdır, bu sabit yalnızca ilerleme göstergesi içindir).
 */
const TOTAL_QUESTIONS = 5;

type Stage = 'setup' | 'in_progress' | 'summary';

function formatTime(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60)
    .toString()
    .padStart(2, '0');
  const seconds = (totalSeconds % 60).toString().padStart(2, '0');
  return `${minutes}:${seconds}`;
}

const difficultyOptions: { value: InterviewDifficulty; label: string }[] = [
  { value: 'junior', label: tr.interview.difficultyJunior },
  { value: 'mid', label: tr.interview.difficultyMid },
];

const categoryOptions: { value: InterviewCategory; label: string }[] = [
  { value: 'algorithmic', label: tr.interview.categoryAlgorithmic },
  { value: 'system', label: tr.interview.categorySystem },
  { value: 'behavioral', label: tr.interview.categoryBehavioral },
];

/**
 * Mülakat simülasyonu (bkz. API_CONTRACT.md §7, TASK-235 + TASK-323).
 */
export function InterviewPage() {
  const [stage, setStage] = useState<Stage>('setup');
  const [targetPosition, setTargetPosition] = useState('');
  const [difficulty, setDifficulty] = useState<InterviewDifficulty>('junior');
  const [category, setCategory] = useState<InterviewCategory>('algorithmic');

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [questionText, setQuestionText] = useState('');
  const [answer, setAnswer] = useState('');
  const [lastAnswered, setLastAnswered] = useState<AnsweredQuestion | null>(null);
  const [nextQuestion, setNextQuestion] = useState<NextQuestion | null>(null);
  const [isComplete, setIsComplete] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  useEffect(() => {
    if (stage !== 'in_progress' || lastAnswered) return undefined;
    const interval = setInterval(() => setElapsedSeconds((seconds) => seconds + 1), 1000);
    return () => clearInterval(interval);
  }, [stage, lastAnswered, questionIndex]);

  const startMutation = useMutation({
    mutationFn: startInterview,
    onSuccess: (data) => {
      setSessionId(data.session_id);
      setQuestionIndex(data.question_index);
      setQuestionText(data.question);
      setAnswer('');
      setLastAnswered(null);
      setNextQuestion(null);
      setIsComplete(false);
      setElapsedSeconds(0);
      setStage('in_progress');
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error) || tr.interview.startError);
    },
  });

  const answerMutation = useMutation({
    mutationFn: (payload: { question_index: number; user_answer: string }) =>
      submitAnswer(sessionId as string, payload),
    onSuccess: (data) => {
      setLastAnswered(data.answered);
      setNextQuestion(data.next_question);
      setIsComplete(data.is_session_complete);
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error) || tr.interview.submitError);
    },
  });

  const summaryQuery = useQuery({
    queryKey: ['interviewSummary', sessionId],
    queryFn: () => getInterviewSummary(sessionId as string),
    enabled: stage === 'summary' && !!sessionId,
  });

  function handleStart(event: FormEvent) {
    event.preventDefault();
    if (!targetPosition.trim()) {
      toast.error(tr.interview.targetPositionRequired);
      return;
    }
    startMutation.mutate({ target_position: targetPosition.trim(), difficulty, category });
  }

  function handleSubmitAnswer(event: FormEvent) {
    event.preventDefault();
    if (!answer.trim()) {
      toast.error(tr.interview.answerRequired);
      return;
    }
    answerMutation.mutate({ question_index: questionIndex, user_answer: answer.trim() });
  }

  function handleNextQuestion() {
    if (!nextQuestion) return;
    setQuestionIndex(nextQuestion.question_index);
    setQuestionText(nextQuestion.question);
    setAnswer('');
    setLastAnswered(null);
    setNextQuestion(null);
    setElapsedSeconds(0);
  }

  function handleNewInterview() {
    setStage('setup');
    setSessionId(null);
    setQuestionIndex(0);
    setQuestionText('');
    setAnswer('');
    setLastAnswered(null);
    setNextQuestion(null);
    setIsComplete(false);
    setElapsedSeconds(0);
  }

  if (stage === 'setup') {
    return (
      <div className="mx-auto max-w-xl space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">{tr.interview.title}</h1>
          <p className="mt-1 text-sm text-gray-500">{tr.interview.subtitle}</p>
        </div>

        <form onSubmit={handleStart} className="card space-y-5">
          <h2 className="text-base font-semibold text-gray-900">{tr.interview.setupTitle}</h2>

          <Input
            label={tr.interview.targetPositionLabel}
            placeholder={tr.interview.targetPositionPlaceholder}
            value={targetPosition}
            onChange={(event) => setTargetPosition(event.target.value)}
          />

          <div>
            <p className="label">{tr.interview.difficultyLabel}</p>
            <div className="flex gap-4">
              {difficultyOptions.map((opt) => (
                <label key={opt.value} className="flex items-center gap-2 text-sm text-gray-700">
                  <input
                    type="radio"
                    name="difficulty"
                    checked={difficulty === opt.value}
                    onChange={() => setDifficulty(opt.value)}
                    className="h-4 w-4 border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </div>

          <div>
            <p className="label">{tr.interview.categoryLabel}</p>
            <div className="flex flex-wrap gap-4">
              {categoryOptions.map((opt) => (
                <label key={opt.value} className="flex items-center gap-2 text-sm text-gray-700">
                  <input
                    type="radio"
                    name="category"
                    checked={category === opt.value}
                    onChange={() => setCategory(opt.value)}
                    className="h-4 w-4 border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </div>

          <div className="flex justify-end">
            <Button type="submit" isLoading={startMutation.isPending}>
              {startMutation.isPending ? tr.interview.starting : tr.interview.startButton}
            </Button>
          </div>
        </form>
      </div>
    );
  }

  if (stage === 'in_progress') {
    return (
      <div className="mx-auto max-w-2xl space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-gray-900">{tr.interview.title}</h1>
          <div className="text-right text-sm text-gray-500">
            <p>{tr.interview.questionProgress(questionIndex + 1, TOTAL_QUESTIONS)}</p>
            <p>
              {tr.interview.timeElapsed}: {formatTime(elapsedSeconds)}
            </p>
          </div>
        </div>

        <div className="h-2 w-full rounded-full bg-gray-100">
          <div
            className="h-2 rounded-full bg-primary-600 transition-all"
            style={{ width: `${Math.min(100, ((questionIndex + 1) / TOTAL_QUESTIONS) * 100)}%` }}
          />
        </div>

        <div className="card">
          <p className="text-base font-medium text-gray-900">{questionText}</p>
        </div>

        {!lastAnswered && (
          <form onSubmit={handleSubmitAnswer} className="card space-y-4">
            <Textarea
              label={tr.interview.answerLabel}
              placeholder={tr.interview.answerPlaceholder}
              rows={6}
              value={answer}
              onChange={(event) => setAnswer(event.target.value)}
            />
            <div className="flex justify-end">
              <Button type="submit" isLoading={answerMutation.isPending}>
                {answerMutation.isPending ? tr.interview.submitting : tr.interview.submitAnswer}
              </Button>
            </div>
          </form>
        )}

        {lastAnswered && (
          <div className="card space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-gray-900">{tr.interview.feedbackTitle}</h2>
              <span className="rounded-full bg-primary-50 px-3 py-1 text-sm font-semibold text-primary-700">
                {tr.interview.scoreLabel}: {lastAnswered.score}/10
              </span>
            </div>
            <p className="text-sm text-gray-700">{lastAnswered.feedback}</p>
            {lastAnswered.correct_answer_hint && (
              <p className="text-sm text-gray-500">
                <span className="font-medium text-gray-700">{tr.interview.correctAnswerHint}:</span>{' '}
                {lastAnswered.correct_answer_hint}
              </p>
            )}

            <div className="flex justify-end">
              {isComplete ? (
                <Button onClick={() => setStage('summary')}>{tr.interview.sessionComplete}</Button>
              ) : (
                <Button onClick={handleNextQuestion}>{tr.interview.nextQuestion}</Button>
              )}
            </div>
          </div>
        )}
      </div>
    );
  }

  // stage === 'summary'
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900">{tr.interview.summaryTitle}</h1>

      {summaryQuery.isLoading && <Spinner label={tr.interview.loadingSummary} />}

      {summaryQuery.isError && (
        <ErrorState
          message={getApiErrorMessage(summaryQuery.error)}
          onRetry={() => summaryQuery.refetch()}
        />
      )}

      {summaryQuery.data && (
        <div className="space-y-4">
          <div className="card flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">{tr.interview.overallScore}</span>
            <span className="text-2xl font-bold text-primary-700">
              {summaryQuery.data.overall_score}
            </span>
          </div>

          <div className="card">
            <h2 className="mb-2 text-sm font-semibold text-gray-900">
              {tr.interview.strengthsTitle}
            </h2>
            <ul className="list-inside list-disc space-y-1 text-sm text-gray-700">
              {summaryQuery.data.strengths.map((strength) => (
                <li key={strength}>{strength}</li>
              ))}
            </ul>
          </div>

          <div className="card">
            <h2 className="mb-2 text-sm font-semibold text-gray-900">
              {tr.interview.improvementsTitle}
            </h2>
            <ul className="list-inside list-disc space-y-1 text-sm text-gray-700">
              {summaryQuery.data.improvements.map((improvement) => (
                <li key={improvement}>{improvement}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <div className="flex justify-end">
        <Button onClick={handleNewInterview}>{tr.interview.newInterview}</Button>
      </div>
    </div>
  );
}
