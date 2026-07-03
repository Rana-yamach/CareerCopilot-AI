import { useState } from 'react';
import type { FormEvent } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { connectGithub, syncGithub } from '@/api/github';
import { getApiErrorMessage } from '@/api/client';
import { useProfile } from '@/hooks/useAuth';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { tr } from '@/i18n/tr';
import type { ConnectGithubResponse } from '@/types/github';

/**
 * GitHub bağlama + dil senkronizasyonu (bkz. API_CONTRACT.md §8, TASK-236).
 * `/settings` route'una yerleştirilmiştir: hesap bağlantısı bir ayar
 * niteliğinde olduğundan Sidebar'daki "Ayarlar" girişiyle tutarlıdır.
 */
export function GithubConnectPage() {
  const { data: profile } = useProfile();
  const queryClient = useQueryClient();
  const [username, setUsername] = useState('');
  const [connected, setConnected] = useState<ConnectGithubResponse | null>(null);

  const connectMutation = useMutation({
    mutationFn: connectGithub,
    onSuccess: (data) => {
      setConnected(data);
      toast.success(tr.github.connectSuccess);
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error) || tr.github.connectError);
    },
  });

  const syncMutation = useMutation({
    mutationFn: syncGithub,
    onSuccess: () => toast.success(tr.github.syncSuccess),
    onError: (error) => {
      toast.error(getApiErrorMessage(error) || tr.github.syncError);
    },
  });

  function handleConnect(event: FormEvent) {
    event.preventDefault();
    if (!username.trim()) {
      toast.error(tr.github.usernameRequired);
      return;
    }
    connectMutation.mutate({ github_username: username.trim() });
  }

  const isConnected = !!connected || !!profile?.github_username;
  const displayUsername = connected?.github_username ?? profile?.github_username ?? '';

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">{tr.github.title}</h1>
        <p className="mt-1 text-sm text-gray-500">{tr.github.subtitle}</p>
      </div>

      <form onSubmit={handleConnect} className="card space-y-4">
        <Input
          label={tr.github.usernameLabel}
          placeholder={tr.github.usernamePlaceholder}
          value={username}
          onChange={(event) => setUsername(event.target.value)}
        />
        {isConnected && <p className="text-xs text-gray-500">{tr.github.reconnectHint}</p>}
        <div className="flex justify-end">
          <Button type="submit" isLoading={connectMutation.isPending}>
            {connectMutation.isPending ? tr.github.connecting : tr.github.connectButton}
          </Button>
        </div>
      </form>

      {isConnected && (
        <div className="card space-y-4">
          <div className="flex items-center gap-4">
            {connected?.avatar_url && (
              <img
                src={connected.avatar_url}
                alt={displayUsername}
                className="h-14 w-14 rounded-full border border-gray-200"
              />
            )}
            <div>
              <p className="text-sm text-gray-500">{tr.github.connectedAs}</p>
              <p className="text-base font-semibold text-gray-900">{displayUsername}</p>
              {connected && (
                <p className="mt-1 text-sm text-gray-500">
                  {tr.github.publicRepos}: {connected.public_repos}
                  {connected.verified && (
                    <span className="ml-2 rounded-full bg-green-50 px-2 py-0.5 text-xs font-medium text-green-700">
                      {tr.github.verified}
                    </span>
                  )}
                </p>
              )}
            </div>
          </div>

          <Button
            type="button"
            variant="secondary"
            onClick={() => syncMutation.mutate()}
            isLoading={syncMutation.isPending}
          >
            {syncMutation.isPending ? tr.github.syncing : tr.github.syncButton}
          </Button>

          {syncMutation.data && (
            <div>
              <h2 className="text-sm font-semibold text-gray-900">{tr.github.languagesTitle}</h2>
              <p className="mb-2 text-xs text-gray-500">
                {tr.github.lastSynced}{' '}
                {new Date(syncMutation.data.synced_at).toLocaleString('tr-TR')}
              </p>
              <div className="space-y-2">
                {Object.entries(syncMutation.data.languages)
                  .sort((a, b) => b[1] - a[1])
                  .map(([lang, pct]) => (
                    <div key={lang}>
                      <div className="flex justify-between text-xs text-gray-600">
                        <span>{lang}</span>
                        <span>%{pct.toFixed(1)}</span>
                      </div>
                      <div className="mt-1 h-2 w-full rounded-full bg-gray-100">
                        <div
                          className="h-2 rounded-full bg-primary-600"
                          style={{ width: `${Math.min(pct, 100)}%` }}
                        />
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>
      )}

      {!isConnected && <p className="text-sm text-gray-500">{tr.github.notConnectedYet}</p>}
    </div>
  );
}
