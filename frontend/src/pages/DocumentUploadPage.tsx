import { useRef, useState } from 'react';
import type { DragEvent } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getLatestDocuments } from '@/api/documents';
import { useDocumentUpload } from '@/hooks/useDocumentUpload';
import { Spinner } from '@/components/ui/Spinner';
import { EmptyState } from '@/components/ui/EmptyState';
import { tr } from '@/i18n/tr';
import type { DocumentSummary, DocumentType } from '@/types/document';

const documentTypeLabel: Record<DocumentType, string> = {
  cv: tr.documents.documentTypeCv,
  linkedin_pdf: tr.documents.documentTypeLinkedin,
  generated_cv: tr.documents.documentTypeGenerated,
};

interface UploadCardProps {
  documentType: DocumentType;
  title: string;
}

function UploadCard({ documentType, title }: UploadCardProps) {
  const { selectAndUpload, uploadMutation, statusQuery } = useDocumentUpload(documentType);
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files?.[0];
    if (file) selectAndUpload(file);
  }

  const status = statusQuery.data?.status;
  const isBusy = uploadMutation.isPending || (!!status && status !== 'completed' && status !== 'failed');

  return (
    <div className="card">
      <h2 className="text-base font-semibold text-gray-900">{title}</h2>

      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click();
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`mt-3 flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-4 py-8 text-center transition-colors ${
          isDragging ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400'
        }`}
      >
        <p className="text-sm font-medium text-gray-700">{tr.documents.dropzoneHint}</p>
        <p className="mt-1 text-xs text-gray-500">{tr.documents.dropzoneFormats}</p>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) selectAndUpload(file);
            e.target.value = '';
          }}
        />
      </div>

      {isBusy && (
        <div className="mt-4 flex items-center gap-3 rounded-lg bg-gray-50 px-3 py-2">
          <span
            className="h-4 w-4 animate-spin rounded-full border-2 border-primary-600 border-t-transparent"
            aria-hidden="true"
          />
          <span className="text-sm text-gray-600">
            {uploadMutation.isPending
              ? tr.documents.uploading
              : status === 'queued'
                ? tr.documents.queued
                : tr.documents.processing}
          </span>
        </div>
      )}

      {status === 'completed' && (
        <p className="mt-4 text-sm font-medium text-green-700">{tr.documents.completed}</p>
      )}

      {status === 'failed' && (
        <p className="mt-4 text-sm font-medium text-red-700">
          {statusQuery.data?.error_message ?? tr.documents.failed}
        </p>
      )}
    </div>
  );
}

function DocumentCard({ doc }: { doc: DocumentSummary }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <span className="rounded-full bg-primary-50 px-2.5 py-0.5 text-xs font-medium text-primary-700">
          {documentTypeLabel[doc.document_type]}
        </span>
        {doc.cv_score !== null && (
          <span className="text-sm font-semibold text-gray-900">
            {tr.documents.cvScore}: {doc.cv_score}
          </span>
        )}
      </div>
      {doc.cv_score_explanation && (
        <p className="mt-2 text-sm text-gray-600">{doc.cv_score_explanation}</p>
      )}
      {(doc.parsed_skills?.languages?.length > 0 ||
        doc.parsed_skills?.frameworks?.length > 0 ||
        doc.parsed_skills?.tools?.length > 0) && (
        <div className="mt-3 space-y-1 text-sm text-gray-600">
          {doc.parsed_skills.languages?.length > 0 && (
            <p>
              <span className="font-medium text-gray-700">{tr.documents.languages}:</span>{' '}
              {doc.parsed_skills.languages.join(', ')}
            </p>
          )}
          {doc.parsed_skills.frameworks?.length > 0 && (
            <p>
              <span className="font-medium text-gray-700">{tr.documents.frameworks}:</span>{' '}
              {doc.parsed_skills.frameworks.join(', ')}
            </p>
          )}
          {doc.parsed_skills.tools?.length > 0 && (
            <p>
              <span className="font-medium text-gray-700">{tr.documents.tools}:</span>{' '}
              {doc.parsed_skills.tools.join(', ')}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export function DocumentUploadPage() {
  const latestDocsQuery = useQuery({
    queryKey: ['latestDocuments'],
    queryFn: getLatestDocuments,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">{tr.documents.title}</h1>
        <p className="mt-1 text-sm text-gray-500">{tr.documents.subtitle}</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <UploadCard documentType="cv" title={tr.documents.uploadCv} />
        <UploadCard documentType="linkedin_pdf" title={tr.documents.uploadLinkedin} />
      </div>

      <div>
        <h2 className="mb-3 text-lg font-semibold text-gray-900">{tr.documents.uploadedDocumentsTitle}</h2>
        {latestDocsQuery.isLoading && <Spinner label={tr.common.loading} />}
        {latestDocsQuery.data && latestDocsQuery.data.documents.length === 0 && (
          <EmptyState title={tr.documents.noDocuments} />
        )}
        {latestDocsQuery.data && latestDocsQuery.data.documents.length > 0 && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {latestDocsQuery.data.documents.map((doc) => (
              <DocumentCard key={doc.document_id} doc={doc} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
