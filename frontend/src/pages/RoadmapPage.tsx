import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { generateRoadmap, getActiveRoadmap, getRoadmap, updateRoadmapTask } from '@/api/roadmap';
import { getLatestSkillGap } from '@/api/skillGap';
import { getApiErrorMessage } from '@/api/client';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Spinner } from '@/components/ui/Spinner';
import { ErrorState } from '@/components/ui/ErrorState';
import { tr } from '@/i18n/tr';
import type { Roadmap, RoadmapWeekPlan } from '@/types/roadmap';

function WeekCard({
  week,
  isExpanded,
  onToggle,
  onTaskToggle,
  isTaskPending,
}: {
  week: RoadmapWeekPlan;
  isExpanded: boolean;
  onToggle: () => void;
  onTaskToggle: (taskId: string, done: boolean) => void;
  isTaskPending: (taskId: string) => boolean;
}) {
  const doneCount = week.tasks.filter((task) => task.done).length;

  return (
    <div className="card">
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center justify-between gap-3 text-left"
        aria-expanded={isExpanded}
      >
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-primary-600">
            {tr.roadmap.weekLabel(week.week)}
          </p>
          <p className="text-base font-semibold text-gray-900">{week.theme}</p>
          <p className="text-xs text-gray-500">
            {doneCount}/{week.tasks.length}
          </p>
        </div>
        <span aria-hidden="true" className="text-lg leading-none text-gray-400">
          {isExpanded ? '−' : '+'}
        </span>
      </button>

      {isExpanded && (
        <ul className="mt-4 space-y-3 border-t border-gray-100 pt-4">
          {week.tasks.map((task) => (
            <li key={task.task_id} className="flex items-start gap-3">
              <input
                type="checkbox"
                className="mt-1 h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                checked={task.done}
                disabled={isTaskPending(task.task_id)}
                onChange={(event) => onTaskToggle(task.task_id, event.target.checked)}
              />
              <div>
                <p
                  className={`text-sm font-medium ${task.done ? 'text-gray-400 line-through' : 'text-gray-800'}`}
                >
                  {task.title}
                </p>
                {task.resource && (
                  <p className="text-xs text-gray-500">{task.resource}</p>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/**
 * Haftalık öğrenme yol haritası (bkz. API_CONTRACT.md §6, TASK-233).
 * `report_id` query param'ı ile (SkillGapPage'den) veya en son beceri
 * boşluğu raporundan otomatik olarak beslenir.
 */
export function RoadmapPage() {
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const skillGapReportIdFromQuery = searchParams.get('report_id');

  const [roadmapId, setRoadmapId] = useState<string | null>(null);
  const [weeklyHours, setWeeklyHours] = useState(10);
  const [expandedWeeks, setExpandedWeeks] = useState<Set<number>>(new Set([1]));

  const activeQuery = useQuery({
    queryKey: ['roadmapActive'],
    queryFn: getActiveRoadmap,
  });

  useEffect(() => {
    if (!roadmapId && activeQuery.data?.roadmap) {
      setRoadmapId(activeQuery.data.roadmap.roadmap_id);
    }
  }, [activeQuery.data, roadmapId]);

  const latestSkillGapQuery = useQuery({
    queryKey: ['skillGapLatestForRoadmap'],
    queryFn: getLatestSkillGap,
    enabled: !skillGapReportIdFromQuery,
  });

  const effectiveReportId =
    skillGapReportIdFromQuery ?? latestSkillGapQuery.data?.report?.report_id ?? null;

  const roadmapQuery = useQuery({
    queryKey: ['roadmap', roadmapId],
    queryFn: () => getRoadmap(roadmapId as string),
    enabled: !!roadmapId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === 'completed' || status === 'failed' ? false : 2000;
    },
  });

  const generateMutation = useMutation({
    mutationFn: generateRoadmap,
    onSuccess: (data) => {
      setRoadmapId(data.roadmap_id);
      toast.success(tr.roadmap.generateSuccess);
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error) || tr.roadmap.generateError);
    },
  });

  const [pendingTaskIds, setPendingTaskIds] = useState<Set<string>>(new Set());

  const taskMutation = useMutation({
    mutationFn: ({ taskId, done }: { taskId: string; done: boolean }) =>
      updateRoadmapTask(roadmapId as string, taskId, { done }),
    onMutate: ({ taskId }) => {
      setPendingTaskIds((prev) => new Set(prev).add(taskId));
    },
    onSuccess: (data) => {
      queryClient.setQueryData<Roadmap | undefined>(['roadmap', roadmapId], (old) => {
        if (!old) return old;
        return {
          ...old,
          progress_percent: data.progress_percent,
          plan: old.plan.map((week) => ({
            ...week,
            tasks: week.tasks.map((task) =>
              task.task_id === data.task_id ? { ...task, done: data.done } : task,
            ),
          })),
        };
      });
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error) || tr.roadmap.taskUpdateError);
    },
    onSettled: (_data, _error, variables) => {
      setPendingTaskIds((prev) => {
        const next = new Set(prev);
        next.delete(variables.taskId);
        return next;
      });
    },
  });

  function handleGenerate(event: FormEvent) {
    event.preventDefault();
    if (!effectiveReportId) {
      toast.error(tr.roadmap.needsSkillGap);
      return;
    }
    if (weeklyHours < 1 || weeklyHours > 40) {
      toast.error(tr.roadmap.weeklyHoursRange);
      return;
    }
    generateMutation.mutate({ skill_gap_report_id: effectiveReportId, weekly_hours: weeklyHours });
  }

  function toggleWeek(week: number) {
    setExpandedWeeks((prev) => {
      const next = new Set(prev);
      if (next.has(week)) next.delete(week);
      else next.add(week);
      return next;
    });
  }

  const roadmap = roadmapQuery.data;
  const isGenerating =
    generateMutation.isPending ||
    (!!roadmap && (roadmap.status === 'queued' || roadmap.status === 'processing'));

  const hasRoadmap = !!roadmap && roadmap.status === 'completed';

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">{tr.roadmap.title}</h1>
        <p className="mt-1 text-sm text-gray-500">{tr.roadmap.subtitle}</p>
      </div>

      {activeQuery.isLoading && !roadmapId && <Spinner label={tr.common.loading} />}

      {isGenerating && (
        <div className="card">
          <Spinner label={tr.roadmap.generating} />
        </div>
      )}

      {!isGenerating && roadmapQuery.isError && (
        <ErrorState
          message={getApiErrorMessage(roadmapQuery.error)}
          onRetry={() => roadmapQuery.refetch()}
        />
      )}

      {!isGenerating && hasRoadmap && roadmap && (
        <div className="space-y-6">
          <div className="card">
            <div className="mb-2 flex items-center justify-between text-sm">
              <span className="font-medium text-gray-700">{tr.roadmap.progressLabel}</span>
              <span className="text-gray-500">
                %{roadmap.progress_percent} · {tr.roadmap.totalWeeks(roadmap.weeks_total)}
              </span>
            </div>
            <div className="h-2.5 w-full rounded-full bg-gray-100">
              <div
                className="h-2.5 rounded-full bg-primary-600 transition-all"
                style={{ width: `${Math.max(0, Math.min(100, roadmap.progress_percent))}%` }}
              />
            </div>
          </div>

          {roadmap.milestones.length > 0 && (
            <div className="card">
              <h2 className="mb-3 text-sm font-semibold text-gray-900">
                {tr.roadmap.milestonesTitle}
              </h2>
              <ul className="space-y-1 text-sm text-gray-600">
                {roadmap.milestones.map((milestone) => (
                  <li key={`${milestone.week}-${milestone.title}`}>
                    <span className="font-medium text-gray-800">
                      {tr.roadmap.weekLabel(milestone.week)}:
                    </span>{' '}
                    {milestone.title}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="space-y-3">
            {[...roadmap.plan]
              .sort((a, b) => a.week - b.week)
              .map((week) => (
                <WeekCard
                  key={week.week}
                  week={week}
                  isExpanded={expandedWeeks.has(week.week)}
                  onToggle={() => toggleWeek(week.week)}
                  onTaskToggle={(taskId, done) => taskMutation.mutate({ taskId, done })}
                  isTaskPending={(taskId) => pendingTaskIds.has(taskId)}
                />
              ))}
          </div>

          <form onSubmit={handleGenerate} className="card flex flex-col gap-4 sm:flex-row sm:items-end">
            <div className="flex-1">
              <Input
                label={tr.roadmap.weeklyHoursLabel}
                type="number"
                min={1}
                max={40}
                value={weeklyHours}
                onChange={(event) => setWeeklyHours(Number(event.target.value))}
              />
            </div>
            <Button type="submit" variant="secondary" isLoading={generateMutation.isPending}>
              {tr.roadmap.regenerateButton}
            </Button>
          </form>
        </div>
      )}

      {!isGenerating && !roadmap && !activeQuery.isLoading && (
        <div className="card space-y-4">
          <p className="text-sm text-gray-600">{tr.roadmap.noActiveRoadmap}</p>

          {effectiveReportId ? (
            <form onSubmit={handleGenerate} className="flex flex-col gap-4 sm:flex-row sm:items-end">
              <div className="flex-1">
                <Input
                  label={tr.roadmap.weeklyHoursLabel}
                  type="number"
                  min={1}
                  max={40}
                  value={weeklyHours}
                  onChange={(event) => setWeeklyHours(Number(event.target.value))}
                />
              </div>
              <Button type="submit" isLoading={generateMutation.isPending}>
                {generateMutation.isPending ? tr.roadmap.generating : tr.roadmap.generateButton}
              </Button>
            </form>
          ) : (
            <div className="space-y-3">
              <p className="text-sm text-gray-500">{tr.roadmap.needsSkillGap}</p>
              <Link to="/skill-gap" className="btn-primary inline-flex">
                {tr.roadmap.goToSkillGap}
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
