import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getDocumentStatus, uploadDocument } from '@/api/documents';
import { getApiErrorMessage } from '@/api/client';
import { tr } from '@/i18n/tr';
import type { DocumentType } from '@/types/document';

const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024; // 5 MB
const ALLOWED_MIME_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
];

/**
 * Belge yükleme + polling akışını yönetir (bkz. TASK-125, ARCHITECTURE.md §11.1).
 */
export function useDocumentUpload(documentType: DocumentType) {
  const [documentId, setDocumentId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadDocument(file, documentType),
    onSuccess: (data) => {
      setDocumentId(data.document_id);
      toast.success(tr.documents.uploadSuccess);
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error) || tr.documents.uploadError);
    },
  });

  const statusQuery = useQuery({
    queryKey: ['documentStatus', documentId],
    queryFn: () => getDocumentStatus(documentId as string),
    enabled: !!documentId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === 'completed' || status === 'failed') {
        queryClient.invalidateQueries({ queryKey: ['latestDocuments'] });
        return false;
      }
      return 2000;
    },
  });

  function validateFile(file: File): string | null {
    if (file.size > MAX_FILE_SIZE_BYTES) {
      return tr.documents.fileTooLarge;
    }
    const isPdfOrDocx =
      ALLOWED_MIME_TYPES.includes(file.type) || /\.(pdf|docx)$/i.test(file.name);
    if (!isPdfOrDocx) {
      return tr.documents.unsupportedFormat;
    }
    return null;
  }

  function selectAndUpload(file: File) {
    const validationError = validateFile(file);
    if (validationError) {
      toast.error(validationError);
      return;
    }
    setDocumentId(null);
    uploadMutation.mutate(file);
  }

  return {
    documentId,
    selectAndUpload,
    uploadMutation,
    statusQuery,
  };
}
