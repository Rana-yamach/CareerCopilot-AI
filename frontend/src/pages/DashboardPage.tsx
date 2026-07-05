import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useProfile } from '@/hooks/useAuth';
import { getLatestDocuments } from '@/api/documents';
import { getActiveRoadmap } from '@/api/roadmap';
import { getLatestSkillGap } from '@/api/skillGap';
import { listInterviewSessions } from '@/api/interview';
import { tr } from '@/i18n/tr';

interface StatCardProps {
  title: string;
  value: string;
  hint?: string;
  action?: { label: string; to: string };
}

function StatCard({ title, value, hint, action }: StatCardProps) {
  return (
    <div className="card flex flex-col justify-between">
      <div>
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <p className="mt-2 text-3xl font-semibold text-gray-900">{value}</p>
        {hint && <p className="mt-1 text-sm text-gray-500">{hint}</p>}
      </div>
      {action && (
        <Link
          to={action.to}
          className="mt-4 text-sm font-medium text-primary-600 hover:text-primary-700"
        >
          {action.label} →
        </Link>
      )}
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
  const cvScoreValue = latestCvDoc ? String(latestCvDoc.cv_score) : '-';

  const skillGapReport = skillGapQuery.data?.report;
  const skillGapValue =
    skillGapReport?.status === 'completed' ? `%${skillGapReport.match_score}` : '-';
  const skillGapHint =
    skillGapReport && skillGapReport.status !== 'completed' && skillGapReport.status !== 'failed'
      ? tr.dashboard.analyzing
      : tr.dashboard.noSkillGap;

  const roadmap = roadmapQuery.data?.roadmap;
  const roadmapValue = roadmap ? `%${roadmap.progress_percent}` : '%0';

  const lastInterview = interviewsQuery.data?.items?.[0];
  const interviewValue = lastInterview ? String(lastInterview.overall_score) : '-';

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">{tr.dashboard.title}</h1>
        <p className="mt-1 text-sm text-gray-500">
          {isLoading ? tr.common.loading : tr.dashboard.welcome(profile?.email ?? '')}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title={tr.dashboard.cvScoreCard}
          value={cvScoreValue}
          hint={latestCvDoc ? undefined : tr.dashboard.noData}
          action={{ label: tr.dashboard.uploadCta, to: '/documents' }}
        />
        <StatCard
          title={tr.dashboard.skillGapCard}
          value={skillGapValue}
          hint={skillGapReport?.status === 'completed' ? undefined : skillGapHint}
          action={{ label: tr.dashboard.startAnalysisCta, to: '/skill-gap' }}
        />
        <StatCard
          title={tr.dashboard.roadmapCard}
          value={roadmapValue}
          hint={roadmap ? undefined : tr.dashboard.noActivePlan}
          action={{ label: tr.dashboard.startRoadmapCta, to: '/roadmap' }}
        />
        <StatCard
          title={tr.dashboard.interviewCard}
          value={interviewValue}
          hint={lastInterview ? undefined : tr.dashboard.noInterview}
          action={{ label: tr.dashboard.startInterviewCta, to: '/interview' }}
        />
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900">{tr.nav.cvBuilder}</h2>
        <p className="mt-1 text-sm text-gray-500">{tr.dashboard.cvBuilderPromo}</p>
        <Link to="/cv/builder/sections" className="btn-primary mt-4 inline-flex">
          {tr.nav.cvBuilder}
        </Link>
      </div>
    </div>
  );
}
