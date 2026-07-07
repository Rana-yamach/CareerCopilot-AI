import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { BarChart3 } from 'lucide-react';
import { analyzeSkillGap, getLatestSkillGap, getSkillGapReport } from '@/api/skillGap';
import { getApiErrorMessage } from '@/api/client';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Spinner } from '@/components/ui/Spinner';
import { ErrorState } from '@/components/ui/ErrorState';
import { EmptyState } from '@/components/ui/EmptyState';
import { tr } from '@/i18n/tr';
import type { MissingSkill } from '@/types/skillGap';

const priorityAccent: Record<number, { bar: string; badge: string }> = {
  1: { bar: 'border-l-rose-500', badge: 'bg-rose-50 text-rose-700 dark:bg-rose-500/15 dark:text-rose-400' },
  2: { bar: 'border-l-rose-500', badge: 'bg-rose-50 text-rose-700 dark:bg-rose-500/15 dark:text-rose-400' },
  3: {
    bar: 'border-l-accent-500',
    badge: 'bg-accent-50 text-accent-700 dark:bg-accent-500/15 dark:text-accent-400',
  },
  4: {
    bar: 'border-l-emerald-500',
    badge: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400',
  },
  5: {
    bar: 'border-l-emerald-500',
    badge: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400',
  },
};

function priorityClass(priority: number): { bar: string; badge: string } {
  return priorityAccent[priority] ?? priorityAccent[3];
}

/**
 * Uyum skoru halkası: `primary` -> `accent` konik gradient ile doldurulur,
 * kalan kısım tema border rengiyle (açık/koyu duyarlı) çizilir.
 */
function MatchScoreGauge({ score }: { score: number }) {
  const clamped = Math.max(0, Math.min(100, score));
  return (
    <div
      className="flex h-32 w-32 shrink-0 items-center justify-center rounded-full shadow-sm"
      style={{
        background: `conic-gradient(from 0deg, #1a56db 0%, #1a56db ${clamped}%, rgb(var(--color-border)) ${clamped}% 100%)`,
      }}
      role="img"
      aria-label={`${tr.skillGap.matchScore}: %${clamped}`}
    >
      <div className="flex h-24 w-24 flex-col items-center justify-center rounded-full bg-surface">
        <span className="text-2xl font-bold text-primary-600 dark:text-primary-400">
          %{clamped}
        </span>
        <span className="text-xs text-faint">{tr.skillGap.matchScore}</span>
      </div>
    </div>
  );
}

function MissingSkillCard({ skill }: { skill: MissingSkill }) {
  const [expanded, setExpanded] = useState(false);
  const accent = priorityClass(skill.priority);
  return (
    <div className={`rounded-xl border border-border border-l-4 bg-surface p-4 ${accent.bar}`}>
      <button
        type="button"
        onClick={() => setExpanded((value) => !value)}
        className="flex w-full items-center justify-between gap-3 text-left"
        aria-expanded={expanded}
      >
        <div>
          <p className="font-semibold text-default">{skill.name}</p>
          <p className="mt-1.5 flex flex-wrap items-center gap-2 text-xs">
            <span className={`rounded-full px-2 py-0.5 font-medium ${accent.badge}`}>
              {tr.skillGap.priority} {skill.priority}
            </span>
            <span className="text-faint">{tr.skillGap.estimatedWeeks(skill.estimated_weeks)}</span>
          </p>
        </div>
        <span aria-hidden="true" className="text-lg leading-none text-faint">
          {expanded ? '−' : '+'}
        </span>
      </button>
      {expanded && (
        <div className="mt-3 space-y-2 border-t border-border pt-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-faint">
            {tr.skillGap.resourcesTitle}
          </p>
          {skill.resources.length === 0 ? (
            <p className="text-sm text-faint">{tr.skillGap.noResources}</p>
          ) : (
            <ul className="space-y-1 text-sm">
              {skill.resources.map((resource) => (
                <li key={`${resource.title}-${resource.url}`}>
                  <a
                    href={resource.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-primary-600 underline decoration-dotted hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
                  >
                    {resource.title}
                  </a>{' '}
                  <span className="text-xs text-faint">({resource.type})</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * Beceri boşluğu analizi (bkz. API_CONTRACT.md §5, TASK-232). Hedef pozisyon
 * girilip analiz başlatılır, `report_id` ile polling yapılır; tamamlanınca
 * uyum skoru ve eksik beceriler listelenir.
 */
export function SkillGapPage() {
  const navigate = useNavigate();
  const [targetPosition, setTargetPosition] = useState('');
  const [reportId, setReportId] = useState<string | null>(null);

  const latestQuery = useQuery({
    queryKey: ['skillGapLatest'],
    queryFn: getLatestSkillGap,
  });

  useEffect(() => {
    if (reportId || !latestQuery.data?.report) return;
    setReportId(latestQuery.data.report.report_id);
    setTargetPosition(latestQuery.data.report.target_position);
  }, [latestQuery.data, reportId]);

  const reportQuery = useQuery({
    queryKey: ['skillGapReport', reportId],
    queryFn: () => getSkillGapReport(reportId as string),
    enabled: !!reportId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === 'completed' || status === 'failed' ? false : 2000;
    },
  });

  const analyzeMutation = useMutation({
    mutationFn: analyzeSkillGap,
    onSuccess: (data) => {
      setReportId(data.report_id);
      toast.success(tr.skillGap.analyzeSuccess);
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error) || tr.skillGap.analyzeError);
    },
  });

  function handleAnalyze(event: FormEvent) {
    event.preventDefault();
    if (!targetPosition.trim()) {
      toast.error(tr.skillGap.targetPositionRequired);
      return;
    }
    analyzeMutation.mutate({ target_position: targetPosition.trim() });
  }

  const report = reportQuery.data;
  const isProcessing =
    analyzeMutation.isPending ||
    (!!report && (report.status === 'queued' || report.status === 'processing'));

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-default">{tr.skillGap.title}</h1>
        <p className="mt-1 text-sm text-faint">{tr.skillGap.subtitle}</p>
      </div>

      <form onSubmit={handleAnalyze} className="card flex flex-col gap-4 sm:flex-row sm:items-end">
        <div className="flex-1">
          <Input
            label={tr.skillGap.targetPositionLabel}
            placeholder={tr.skillGap.targetPositionPlaceholder}
            value={targetPosition}
            onChange={(event) => setTargetPosition(event.target.value)}
          />
        </div>
        <Button type="submit" isLoading={analyzeMutation.isPending} className="gap-2.5">
          {!analyzeMutation.isPending && (
            <span
              aria-hidden="true"
              className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-white/20"
            >
              <BarChart3 className="h-3.5 w-3.5" />
            </span>
          )}
          {analyzeMutation.isPending ? tr.skillGap.analyzing : tr.skillGap.analyzeButton}
        </Button>
      </form>

      {latestQuery.isLoading && !reportId && <Spinner label={tr.common.loading} />}

      {isProcessing && (
        <div className="card">
          <Spinner label={tr.skillGap.analyzing} />
          <p className="text-center text-sm text-faint">{tr.skillGap.analyzingHint}</p>
        </div>
      )}

      {!isProcessing && reportQuery.isError && (
        <ErrorState
          message={getApiErrorMessage(reportQuery.error)}
          onRetry={() => reportQuery.refetch()}
        />
      )}

      {!isProcessing && report?.status === 'failed' && (
        <ErrorState message={tr.skillGap.reportFailed} onRetry={() => reportQuery.refetch()} />
      )}

      {!isProcessing && report?.status === 'completed' && (
        <div className="space-y-6">
          <div className="card flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
            <MatchScoreGauge score={report.match_score} />
            <div className="flex-1 text-center sm:text-left">
              <p className="text-sm text-faint">{tr.skillGap.lastAnalyzed}</p>
              <p className="text-base font-medium text-default">
                {new Date(report.generated_at).toLocaleString('tr-TR')}
              </p>
              <p className="mt-2 text-sm text-muted">{report.target_position}</p>
            </div>
          </div>

          <div>
            <h2 className="mb-3 text-lg font-semibold text-default">
              {tr.skillGap.missingSkillsTitle}
            </h2>
            <div className="space-y-3">
              {report.missing_skills.map((skill) => (
                <MissingSkillCard key={skill.name} skill={skill} />
              ))}
            </div>
          </div>

          <div className="flex justify-end">
            <Button onClick={() => navigate(`/roadmap?report_id=${report.report_id}`)}>
              {tr.skillGap.createRoadmapButton}
            </Button>
          </div>
        </div>
      )}

      {!isProcessing && !report && !latestQuery.isLoading && (
        <EmptyState title={tr.skillGap.noReportYet} />
      )}
    </div>
  );
}
