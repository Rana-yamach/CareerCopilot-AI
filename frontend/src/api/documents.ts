import { apiClient } from './client';
import type {
  DocumentListResponse,
  DocumentStatusResponse,
  DocumentType,
  LatestDocumentsResponse,
  UploadDocumentResponse,
} from '@/types/document';

export async function uploadDocument(
  file: File,
  documentType: DocumentType,
): Promise<UploadDocumentResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('document_type', documentType);

  const { data } = await apiClient.post<UploadDocumentResponse>('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function getDocumentStatus(docId: string): Promise<DocumentStatusResponse> {
  const { data } = await apiClient.get<DocumentStatusResponse>(`/documents/${docId}/status`);
  return data;
}

export async function getLatestDocuments(): Promise<LatestDocumentsResponse> {
  const { data } = await apiClient.get<LatestDocumentsResponse>('/documents/latest');
  return data;
}

export async function listDocuments(params?: {
  document_type?: DocumentType;
  limit?: number;
  offset?: number;
}): Promise<DocumentListResponse> {
  const { data } = await apiClient.get<DocumentListResponse>('/documents', { params });
  return data;
}

export async function deleteDocument(docId: string): Promise<void> {
  await apiClient.delete(`/documents/${docId}`);
}
