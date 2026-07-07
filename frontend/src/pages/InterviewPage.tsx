import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Headphones, Rocket, Search, SignalLow, SignalMedium } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { getInterviewSummary, startInterview, submitAnswer } from '@/api/interview';
import { getApiErrorMessage } from '@/api/client';
import { Button } from '@/components/ui/Button';
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

const difficultyOptions: { value: InterviewDifficulty; label: string; icon: LucideIcon }[] = [
  { value: 'junior', label: tr.interview.difficultyJunior, icon: SignalLow },
  { value: 'mid', label: tr.interview.difficultyMid, icon: SignalMedium },
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
          <h1 className="text-2xl font-semibold text-default">{tr.interview.title}</h1>
          <p className="mt-1 text-sm text-faint">{tr.interview.subtitle}</p>
        </div>

        <form onSubmit={handleStart} className="card space-y-5">
          <div className="flex items-center gap-3 border-b border-border pb-4">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary-50 text-primary-600 dark:bg-primary-500/15 dark:text-primary-400">
              <Headphones aria-hidden="true" className="h-5 w-5" />
            </span>
            <div>
              <h2 className="text-base font-semibold text-default">{tr.interview.setupTitle}</h2>
              <p className="text-sm text-faint">{tr.interview.setupSubtitle}</p>
            </div>
          </div>

          <div>
            <p className="label uppercase tracking-wide text-xs">{tr.interview.targetPositionLabel}</p>
            <div className="relative">
              <input
                type="text"
                placeholder={tr.interview.targetPositionPlaceholder}
                value={targetPosition}
                onChange={(event) => setTargetPosition(event.target.value)}
                className="input-field pr-10"
              />
              <Search
                aria-hidden="true"
                className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-faint"
              />
            </div>
          </div>

          <div>
            <p className="label uppercase tracking-wide text-xs">{tr.interview.difficultyLabel}</p>
            <div className="grid grid-cols-2 gap-3">
              {difficultyOptions.map((opt) => {
                const Icon = opt.icon;
                const selected = difficulty === opt.value;
                return (
                  <label
                    key={opt.value}
                    className={`flex cursor-pointer flex-col items-center gap-1.5 rounded-xl border px-3 py-3 text-sm font-medium transition-colors ${
                      selected
                        ? 'border-primary-400 bg-primary-50 text-primary-700 dark:border-primary-500/60 dark:bg-primary-500/10 dark:text-primary-300'
                        : 'border-border text-muted hover:border-primary-300 hover:bg-primary-50/40 dark:hover:bg-primary-500/10'
                    }`}
                  >
                    <input
                      type="radio"
                      name="difficulty"
                      className="sr-only"
                      checked={selected}
                      onChange={() => setDifficulty(opt.value)}
                    />
                    <Icon aria-hidden="true" className="h-4 w-4" />
                    {opt.label}
                  </label>
                );
              })}
            </div>
          </div>

          <div>
            <p className="label uppercase tracking-wide text-xs">{tr.interview.categoryLabel}</p>
            <div className="flex flex-wrap gap-4">
              {categoryOptions.map((opt) => (
                <label key={opt.value} className="flex items-center gap-2 text-sm text-muted">
                  <input
                    type="radio"
                    name="category"
                    checked={category === opt.value}
                    onChange={() => setCategory(opt.value)}
                    className="h-4 w-4 border-border text-primary-600 focus:ring-primary-500"
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </div>

          <Button type="submit" isLoading={startMutation.isPending} className="w-full gap-2">
            {startMutation.isPending ? tr.interview.starting : tr.interview.startButton}
            {!startMutation.isPending && <Rocket aria-hidden="true" className="h-4 w-4" />}
          </Button>
        </form>
      </div>
    );
  }

  if (stage === 'in_progress') {
    return (
      <div className="mx-auto max-w-2xl space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-default">{tr.interview.title}</h1>
          <div className="text-right text-sm text-faint">
            <p>{tr.interview.questionProgress(questionIndex + 1, TOTAL_QUESTIONS)}</p>
            <p>
              {tr.interview.timeElapsed}: {formatTime(elapsedSeconds)}
            </p>
          </div>
        </div>

        <div className="h-2 w-full rounded-full bg-surface-2">
          <div
            className="h-2 rounded-full bg-gradient-to-r from-primary-500 to-accent-500 transition-all"
            style={{ width: `${Math.min(100, ((questionIndex + 1) / TOTAL_QUESTIONS) * 100)}%` }}
          />
        </div>

        <div className="card relative overflow-hidden">
          <span
            aria-hidden="true"
            className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-primary-500 to-accent-500"
          />
          <p className="pt-1 text-base font-medium text-default">{questionText}</p>
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
              <h2 className="text-sm font-semibold text-default">{tr.interview.feedbackTitle}</h2>
              <span className="rounded-full bg-primary-50 px-3 py-1 text-sm font-semibold text-primary-700 dark:bg-primary-500/15 dark:text-primary-300">
                {tr.interview.scoreLabel}: {lastAnswered.score}/10
              </span>
            </div>
            <p className="text-sm text-muted">{lastAnswered.feedback}</p>
            {lastAnswered.correct_answer_hint && (
              <p className="text-sm text-faint">
                <span className="font-medium text-muted">{tr.interview.correctAnswerHint}:</span>{' '}
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
      <h1 className="text-2xl font-semibold text-default">{tr.interview.summaryTitle}</h1>

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
            <span className="text-sm font-medium text-muted">{tr.interview.overallScore}</span>
            <span className="bg-gradient-to-r from-primary-600 to-accent-500 bg-clip-text text-2xl font-bold text-transparent">
              {summaryQuery.data.overall_score}
            </span>
          </div>

          <div className="card">
            <h2 className="mb-2 text-sm font-semibold text-default">
              {tr.interview.strengthsTitle}
            </h2>
            <ul className="list-inside list-disc space-y-1 text-sm text-muted">
              {summaryQuery.data.strengths.map((strength) => (
                <li key={strength}>{strength}</li>
              ))}
            </ul>
          </div>

          <div className="card">
            <h2 className="mb-2 text-sm font-semibold text-default">
              {tr.interview.improvementsTitle}
            </h2>
            <ul className="list-inside list-disc space-y-1 text-sm text-muted">
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
