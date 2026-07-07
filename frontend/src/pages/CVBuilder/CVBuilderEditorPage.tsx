import { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { AlertTriangle } from 'lucide-react';
import { downloadCvPdf, exportCVPdf, getCVDraft, updateCVDraft } from '@/api/cv';
import { getApiErrorMessage } from '@/api/client';
import { Spinner } from '@/components/ui/Spinner';
import { ErrorState } from '@/components/ui/ErrorState';
import { Button } from '@/components/ui/Button';
import { tr } from '@/i18n/tr';

type EditorLanguage = 'tr' | 'en';

function autoResize(el: HTMLTextAreaElement | null) {
  if (!el) return;
  el.style.height = 'auto';
  el.style.height = `${el.scrollHeight}px`;
}

function tabClass(active: boolean): string {
  return `px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
    active
      ? 'border-primary-600 text-primary-700 dark:text-primary-400'
      : 'border-transparent text-faint hover:text-muted'
  }`;
}

function languageLabel(lang: EditorLanguage): string {
  return lang === 'tr' ? tr.cvBuilder.editorTabTr : tr.cvBuilder.editorTabEn;
}

/**
 * Backend `user_edited_text`'i tek bir alanda saklar (API_CONTRACT.md §4) —
 * TR ve EN için ayrı alan yoktur. Bu yüzden hangi dilin en son kaydedildiği
 * localStorage'da (draft başına) izlenir; sayfa yeniden yüklendiğinde
 * `user_edited_text` yalnızca o dile atanır, diğer sekme orijinal üretilmiş
 * metni gösterir. Böylece iki dil birbirinin üzerine yazılmaz.
 */
function savedLangStorageKey(draftId: string): string {
  return `cv-editor-saved-lang-${draftId}`;
}

function readSavedLangHint(draftId: string): EditorLanguage | null {
  const value = localStorage.getItem(savedLangStorageKey(draftId));
  return value === 'tr' || value === 'en' ? value : null;
}

function writeSavedLangHint(draftId: string, lang: EditorLanguage) {
  localStorage.setItem(savedLangStorageKey(draftId), lang);
}

/**
 * CV taslağı inline editörü (bkz. API_CONTRACT.md §4, TASK-231).
 * `status="generated"` (veya `"exported"`) olana kadar polling ile bekler;
 * ardından `text_tr`/`text_en` düzenlenebilir hale gelir ve değişiklikler
 * 1 sn debounce ile `PATCH /cv/draft/{id}` üzerinden kaydedilir. TR/EN
 * zamanlayıcıları birbirinden bağımsızdır ki bir dilde yazarken diğer dile
 * geçmek bekleyen kaydı iptal etmesin.
 */
export function CVBuilderEditorPage() {
  const { draftId } = useParams<{ draftId: string }>();

  const [activeLang, setActiveLang] = useState<EditorLanguage>('tr');
  const [editedTr, setEditedTr] = useState('');
  const [editedEn, setEditedEn] = useState('');
  const [savedLang, setSavedLang] = useState<EditorLanguage | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const initializedRef = useRef(false);
  const debounceRef = useRef<Record<EditorLanguage, ReturnType<typeof setTimeout> | null>>({
    tr: null,
    en: null,
  });
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const draftQuery = useQuery({
    queryKey: ['cvDraft', draftId],
    queryFn: () => getCVDraft(draftId as string),
    enabled: !!draftId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === 'generated' || status === 'exported' ? false : 2000;
    },
  });

  const draft = draftQuery.data;

  useEffect(() => {
    if (!draft || !draftId || initializedRef.current) return;
    if (draft.status === 'draft') return;

    const edited = draft.user_edited_text;
    if (edited) {
      const hint = readSavedLangHint(draftId) ?? (draft.output_language === 'en' ? 'en' : 'tr');
      if (hint === 'tr') {
        setEditedTr(edited);
        setEditedEn(draft.text_en ?? '');
      } else {
        setEditedEn(edited);
        setEditedTr(draft.text_tr ?? '');
      }
      setSavedLang(hint);
      setActiveLang(hint);
    } else {
      setEditedTr(draft.text_tr ?? '');
      setEditedEn(draft.text_en ?? '');
      setActiveLang(draft.output_language === 'en' ? 'en' : 'tr');
    }
    initializedRef.current = true;
  }, [draft, draftId]);

  useEffect(() => {
    autoResize(textareaRef.current);
  }, [activeLang, editedTr, editedEn]);

  const updateMutation = useMutation({
    mutationFn: ({ lang, text }: { lang: EditorLanguage; text: string }) =>
      updateCVDraft(draftId as string, { user_edited_text: text }).then(() => lang),
    onSuccess: (lang) => {
      if (draftId) writeSavedLangHint(draftId, lang);
      setSavedLang(lang);
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error) || tr.cvBuilder.editorSaveError);
    },
  });

  function scheduleSave(lang: EditorLanguage, text: string) {
    const timers = debounceRef.current;
    if (timers[lang]) clearTimeout(timers[lang] as ReturnType<typeof setTimeout>);
    timers[lang] = setTimeout(() => {
      updateMutation.mutate({ lang, text });
    }, 1000);
  }

  useEffect(() => {
    const timers = debounceRef.current;
    return () => {
      (Object.keys(timers) as EditorLanguage[]).forEach((lang) => {
        const timer = timers[lang];
        if (timer) clearTimeout(timer);
      });
    };
  }, []);

  function handleTextChange(value: string) {
    if (activeLang === 'tr') setEditedTr(value);
    else setEditedEn(value);
    scheduleSave(activeLang, value);
  }

  async function handleDownloadPdf() {
    if (!draftId) return;
    if (savedLang && savedLang !== activeLang) {
      toast(tr.cvBuilder.editorLanguageMismatchWarning, {
        icon: <AlertTriangle aria-hidden="true" className="h-4 w-4 text-amber-500" />,
      });
    }
    setIsDownloading(true);
    try {
      const exportRes = await exportCVPdf({ draft_id: draftId, language: activeLang });
      const blob = await downloadCvPdf(exportRes.download_url);
      const blobUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = `cv_${draftId}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(blobUrl), 0);
      toast.success(tr.cvBuilder.editorDownloadSuccess);
    } catch (error) {
      toast.error(getApiErrorMessage(error) || tr.cvBuilder.editorDownloadError);
    } finally {
      setIsDownloading(false);
    }
  }

  if (draftQuery.isLoading) {
    return <Spinner label={tr.common.loading} />;
  }

  if (draftQuery.isError) {
    return (
      <ErrorState
        message={getApiErrorMessage(draftQuery.error)}
        onRetry={() => draftQuery.refetch()}
      />
    );
  }

  if (!draft || draft.status === 'draft') {
    return (
      <div className="mx-auto max-w-2xl">
        <Spinner label={tr.cvBuilder.editorGenerating} />
        <p className="text-center text-sm text-faint">{tr.cvBuilder.editorGeneratingHint}</p>
      </div>
    );
  }

  const currentText = activeLang === 'tr' ? editedTr : editedEn;

  return (
    <div className="mx-auto max-w-3xl space-y-4 pb-10">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold text-default">{tr.cvBuilder.editorTitle}</h1>
        <Button onClick={handleDownloadPdf} isLoading={isDownloading}>
          {isDownloading ? tr.cvBuilder.editorDownloading : tr.cvBuilder.editorDownloadPdf}
        </Button>
      </div>

      {draft.output_language === 'both' && (
        <>
          <div className="flex gap-2 border-b border-border">
            <button type="button" onClick={() => setActiveLang('tr')} className={tabClass(activeLang === 'tr')}>
              {tr.cvBuilder.editorTabTr}
            </button>
            <button type="button" onClick={() => setActiveLang('en')} className={tabClass(activeLang === 'en')}>
              {tr.cvBuilder.editorTabEn}
            </button>
          </div>
          {savedLang && (
            <p className="text-xs text-amber-600 dark:text-amber-400">
              {tr.cvBuilder.editorBothLanguageNotice(languageLabel(savedLang))}
            </p>
          )}
        </>
      )}

      <div className="card">
        <div className="mb-2 flex items-center justify-between">
          <label htmlFor="cv-editor-textarea" className="label mb-0">
            {tr.cvBuilder.editorTextareaLabel}
          </label>
          <span className="text-xs text-faint" role="status">
            {updateMutation.isPending
              ? tr.cvBuilder.editorSaving
              : updateMutation.isSuccess
                ? tr.cvBuilder.editorSaved
                : ''}
          </span>
        </div>
        <textarea
          id="cv-editor-textarea"
          ref={textareaRef}
          value={currentText}
          onChange={(event) => handleTextChange(event.target.value)}
          placeholder={tr.cvBuilder.editorEmptyText}
          className="input-field min-h-[420px] resize-none overflow-hidden font-mono text-sm leading-relaxed"
        />
      </div>

      <p className="text-xs text-faint">
        {tr.cvBuilder.editorDraftStatus} <span className="font-medium text-muted">{draft.status}</span>
      </p>
    </div>
  );
}
