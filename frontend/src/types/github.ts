/** API_CONTRACT.md §8 GitHub */
import type { GithubProjectImport } from './cv';

export interface ConnectGithubRequest {
  github_username: string;
}

export interface ConnectGithubResponse {
  github_username: string;
  public_repos: number;
  avatar_url: string;
  verified: boolean;
}

export interface GithubSyncResponse {
  github_username: string;
  languages: Record<string, number>;
  total_public_repos: number;
  synced_at: string;
}

export interface GithubProjectsResponse {
  projects: GithubProjectImport[];
  count: number;
}
