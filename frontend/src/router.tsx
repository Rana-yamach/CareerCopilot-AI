import { createBrowserRouter, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { AppLayout } from '@/components/layout/AppLayout';
import { LoginPage } from '@/pages/LoginPage';
import { RegisterPage } from '@/pages/RegisterPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { DocumentUploadPage } from '@/pages/DocumentUploadPage';
import { SectionSelectPage } from '@/pages/CVBuilder/SectionSelectPage';
import { CVBuilderFormPage } from '@/pages/CVBuilder/CVBuilderFormPage';
import { CVBuilderEditorPage } from '@/pages/CVBuilder/CVBuilderEditorPage';
import { SkillGapPage } from '@/pages/SkillGapPage';
import { RoadmapPage } from '@/pages/RoadmapPage';
import { InterviewPage } from '@/pages/InterviewPage';
import { ChatPage } from '@/pages/ChatPage';
import { GithubConnectPage } from '@/pages/GithubConnectPage';
import { NotFoundPage } from '@/pages/NotFoundPage';

export const router = createBrowserRouter([
  { path: '/', element: <Navigate to="/dashboard" replace /> },
  { path: '/login', element: <LoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: '/dashboard', element: <DashboardPage /> },
          { path: '/documents', element: <DocumentUploadPage /> },
          { path: '/cv/builder/sections', element: <SectionSelectPage /> },
          { path: '/cv/builder/form', element: <CVBuilderFormPage /> },
          { path: '/cv/builder/editor/:draftId', element: <CVBuilderEditorPage /> },
          { path: '/skill-gap', element: <SkillGapPage /> },
          { path: '/roadmap', element: <RoadmapPage /> },
          { path: '/interview', element: <InterviewPage /> },
          { path: '/chat', element: <ChatPage /> },
          { path: '/settings', element: <GithubConnectPage /> },
        ],
      },
    ],
  },
  { path: '*', element: <NotFoundPage /> },
]);
