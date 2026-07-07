import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowRight, FileEdit, FileText, Map, Mic, Sparkles, Target } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { useProfile } from '@/hooks/useAuth';
import { getLatestDocuments } from '@/api/documents';
import { getActiveRoadmap } from '@/api/roadmap';
import { getLatestSkillGap } from '@/api/skillGap';
import { listInterviewSessions } from '@/api/interview';
import { tr } from '@/i18n/tr';

type Tint = 'primary' | 'emerald' | 'accent' | 'rose';

const tintClasses: Record<Tint, { badge: string; icon: string }> = {
  primary: {
    badge: 'bg-primary-50 dark:bg-primary-500/15',
    icon: 'text-primary-600 dark:text-primary-400',
  },
  emerald: {
    badge: 'bg-emerald-50 dark:bg-emerald-500/15',
    icon: 'text-emerald-600 dark:text-emerald-400',
  },
  accent: {
    badge: 'bg-accent-50 dark:bg-accent-500/15',
    icon: 'text-accent-600 dark:text-accent-400',
  },
  rose: {
    badge: 'bg-rose-50 dark:bg-rose-500/15',
    icon: 'text-rose-600 dark:text-rose-400',
  },
};

interface StatCardShellProps {
  title: string;
  icon: LucideIcon;
  tint: Tint;
  action?: { label: string; to: string };
  children: ReactNode;
}

function StatCardShell({ title, icon: Icon, tint, action, children }: StatCardShellProps) {
  const t = tintClasses[tint];
  return (
    <div className="card card-hover flex flex-col justify-between">
      <div>
        <div className="flex items-center gap-3">
          <span
            aria-hidden="true"
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${t.badge}`}
          >
            <Icon aria-hidden="true" className={`h-5 w-5 ${t.icon}`} />
          </span>
          <p className="text-sm font-medium text-muted">{title}</p>
        </div>
        <div className="mt-4">{children}</div>
      </div>
      {action && (
        <Link
          to={action.to}
          className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
        >
          {action.label}
          <ArrowRight aria-hidden="true" className="h-4 w-4" />
        </Link>
      )}
    </div>
  );
}

function MiniRing({ value }: { value: number | null }) {
  const pct = value === null ? 0 : Math.max(0, Math.min(100, value));
  return (
    <div
      className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full"
      style={{
        background:
          value === null
            ? 'rgb(var(--color-border))'
            : `conic-gradient(from 0deg, #1a56db 0%, #1a56db ${pct}%, rgb(var(--color-border)) ${pct}% 100%)`,
      }}
      role="img"
      aria-label={`${tr.dashboard.cvScoreCard}: ${value === null ? tr.dashboard.noData : `${value}/100`}`}
    >
      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-surface text-xs font-semibold text-default">
        {value === null ? '–' : value}
      </div>
    </div>
  );
}

/**
 * Panel: gerçek API verileriyle beslenir (bkz. API_CONTRACT.md §3/§5/§6/§7,
 * TASK-237). Veri yoksa/işleniyorsa Türkçe boş-durum ipucu ve CTA gösterilir.
 */
export function DashboardPage() {
  const { data: profile, isLoading } = useProfile();

  const documentsQuery = useQuery({
    queryKey: ['latestDocuments'],
    queryFn: getLatestDocuments,
  });
  const roadmapQuery = useQuery({ queryKey: ['roadmapActive'], queryFn: getActiveRoadmap });
  const skillGapQuery = useQuery({ queryKey: ['skillGapLatest'], queryFn: getLatestSkillGap });
  const interviewsQuery = useQuery({
    queryKey: ['interviewSessions', 1],
    queryFn: () => listInterviewSessions({ limit: 1 }),
  });

  const latestCvDoc = [...(documentsQuery.data?.documents ?? [])]
    .filter((doc) => doc.cv_score !== null)
    .sort((a, b) => new Date(b.uploaded_at).getTime() - new Date(a.uploaded_at).getTime())[0];
  const cvScoreValue = latestCvDoc ? latestCvDoc.cv_score : null;

  const skillGapReport = skillGapQuery.data?.report;
  const skillGapValue =
    skillGapReport?.status === 'completed' ? `%${skillGapReport.match_score}` : '-';
  const skillGapHint =
    skillGapReport && skillGapReport.status !== 'completed' && skillGapReport.status !== 'failed'
      ? tr.dashboard.analyzing
      : tr.dashboard.noSkillGap;

  const roadmap = roadmapQuery.data?.roadmap;
  const roadmapTasks = roadmap?.plan.flatMap((week) => week.tasks) ?? [];
  const roadmapDone = roadmapTasks.filter((task) => task.done).length;
  const roadmapProgress = roadmap?.progress_percent ?? 0;

  const lastInterview = interviewsQuery.data?.items?.[0];
  const interviewValue = lastInterview ? lastInterview.overall_score : null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-default">{tr.dashboard.title}</h1>
        <p className="mt-1 text-sm text-muted">
          {isLoading ? tr.common.loading : tr.dashboard.welcome(profile?.email ?? '')}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCardShell
          title={tr.dashboard.cvScoreCard}
          icon={FileText}
          tint="primary"
          action={{ label: tr.dashboard.uploadCta, to: '/documents' }}
        >
          <div className="flex items-center gap-4">
            <MiniRing value={cvScoreValue} />
            {cvScoreValue !== null ? (
              <p className="text-2xl font-bold text-default">
                {cvScoreValue}
                <span className="text-sm font-medium text-faint">/100</span>
              </p>
            ) : (
              <p className="text-sm text-faint">{tr.dashboard.noData}</p>
            )}
          </div>
        </StatCardShell>

        <StatCardShell
          title={tr.dashboard.skillGapCard}
          icon={Target}
          tint="emerald"
          action={{ label: tr.dashboard.startAnalysisCta, to: '/skill-gap' }}
        >
          <p className="text-3xl font-bold text-default">{skillGapValue}</p>
          <p className="mt-1 truncate text-sm text-muted">
            {skillGapReport?.status === 'completed' ? skillGapReport.target_position : skillGapHint}
          </p>
        </StatCardShell>

        <StatCardShell
          title={tr.dashboard.roadmapCard}
          icon={Map}
          tint="accent"
          action={{ label: tr.dashboard.startRoadmapCta, to: '/roadmap' }}
        >
          {roadmap ? (
            <>
              <p className="text-2xl font-bold text-default">
                {roadmapDone}
                <span className="text-sm font-medium text-faint">
                  /{roadmapTasks.length} {tr.dashboard.stepsLabel}
                </span>
              </p>
              <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-surface-2">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-primary-500 to-accent-500 transition-all"
                  style={{ width: `${roadmapProgress}%` }}
                />
              </div>
            </>
          ) : (
            <p className="text-sm text-faint">{tr.dashboard.noActivePlan}</p>
          )}
        </StatCardShell>

        <StatCardShell
          title={tr.dashboard.interviewCard}
          icon={Mic}
          tint="rose"
          action={{ label: tr.dashboard.startInterviewCta, to: '/interview' }}
        >
          <p className="text-3xl font-bold text-default">{interviewValue ?? '-'}</p>
          <p className="mt-1 text-sm text-muted">
            {interviewValue !== null ? tr.dashboard.interviewQuality(interviewValue) : tr.dashboard.noInterview}
          </p>
        </StatCardShell>
      </div>

      <div className="card overflow-hidden">
        <span className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 text-white shadow-sm">
          <FileEdit aria-hidden="true" className="h-5 w-5" />
        </span>
        <h2 className="mt-3 text-lg font-semibold text-default">{tr.dashboard.cvBuilderHeroTitle}</h2>
        <p className="mt-2 max-w-2xl text-sm text-muted">{tr.dashboard.cvBuilderPromo}</p>
        <Link to="/cv/builder/sections" className="btn-primary mt-4 inline-flex items-center gap-2">
          {tr.dashboard.startCvBuilderCta}
          <Sparkles aria-hidden="true" className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}
