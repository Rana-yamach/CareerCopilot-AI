import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { analyzeSkillGap, getLatestSkillGap, getSkillGapReport } from '@/api/skillGap';
import { getApiErrorMessage } from '@/api/client';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Spinner } from '@/components/ui/Spinner';
import { ErrorState } from '@/components/ui/ErrorState';
import { EmptyState } from '@/components/ui/EmptyState';
import { tr } from '@/i18n/tr';
import type { MissingSkill } from '@/types/skillGap';

const priorityColor: Record<number, string> = {
  1: 'border-red-300 bg-red-50 text-red-700',
  2: 'border-red-300 bg-red-50 text-red-700',
  3: 'border-amber-300 bg-amber-50 text-amber-700',
  4: 'border-green-300 bg-green-50 text-green-700',
  5: 'border-green-300 bg-green-50 text-green-700',
};

function priorityClass(priority: number): string {
  return priorityColor[priority] ?? priorityColor[3];
}

function MatchScoreGauge({ score }: { score: number }) {
  const clamped = Math.max(0, Math.min(100, score));
  return (
    <div
      className="flex h-32 w-32 shrink-0 items-center justify-center rounded-full"
      style={{ background: `conic-gradient(#4f46e5 ${clamped * 3.6}deg, #e5e7eb 0deg)` }}
      role="img"
      aria-label={`${tr.skillGap.matchScore}: %${clamped}`}
    >
      <div className="flex h-24 w-24 flex-col items-center justify-center rounded-full bg-white">
        <span className="text-2xl font-bold text-gray-900">%{clamped}</span>
        <span className="text-xs text-gray-500">{tr.skillGap.matchScore}</span>
      </div>
    </div>
  );
}

function MissingSkillCard({ skill }: { skill: MissingSkill }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className={`rounded-xl border p-4 ${priorityClass(skill.priority)}`}>
      <button
        type="button"
        onClick={() => setExpanded((value) => !value)}
        className="flex w-full items-center justify-between gap-3 text-left"
        aria-expanded={expanded}
      >
        <div>
          <p className="font-semibold">{skill.name}</p>
          <p className="text-xs opacity-80">
            {tr.skillGap.priority} {skill.priority} · {tr.skillGap.estimatedWeeks(skill.estimated_weeks)}
          </p>
        </div>
        <span aria-hidden="true" className="text-lg leading-none">
          {expanded ? '−' : '+'}
        </span>
      </button>
      {expanded && (
        <div className="mt-3 space-y-2 border-t border-current/20 pt-3">
          <p className="text-xs font-semibold uppercase tracking-wide opacity-80">
            {tr.skillGap.resourcesTitle}
          </p>
          {skill.resources.length === 0 ? (
            <p className="text-sm opacity-80">{tr.skillGap.noResources}</p>
          ) : (
            <ul className="space-y-1 text-sm">
              {skill.resources.map((resource) => (
                <li key={`${resource.title}-${resource.url}`}>
                  <a
                    href={resource.url}
                    target="_blank"
                    rel="noreferrer"
                    className="underline decoration-dotted hover:opacity-80"
                  >
                    {resource.title}
                  </a>{' '}
                  <span className="text-xs opacity-70">({resource.type})</span>
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
        <h1 className="text-2xl font-semibold text-gray-900">{tr.skillGap.title}</h1>
        <p className="mt-1 text-sm text-gray-500">{tr.skillGap.subtitle}</p>
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
        <Button type="submit" isLoading={analyzeMutation.isPending}>
          {analyzeMutation.isPending ? tr.skillGap.analyzing : tr.skillGap.analyzeButton}
        </Button>
      </form>

      {latestQuery.isLoading && !reportId && <Spinner label={tr.common.loading} />}

      {isProcessing && (
        <div className="card">
          <Spinner label={tr.skillGap.analyzing} />
          <p className="text-center text-sm text-gray-500">{tr.skillGap.analyzingHint}</p>
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
              <p className="text-sm text-gray-500">{tr.skillGap.lastAnalyzed}</p>
              <p className="text-base font-medium text-gray-900">
                {new Date(report.generated_at).toLocaleString('tr-TR')}
              </p>
              <p className="mt-2 text-sm text-gray-600">{report.target_position}</p>
            </div>
          </div>

          <div>
            <h2 className="mb-3 text-lg font-semibold text-gray-900">
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
