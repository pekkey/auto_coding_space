import { useState, useEffect } from 'react';
import { api } from '../api';

interface GitHubRepo {
  name: string;
  path: string;
  url: string;
  branch: string;
}

interface GitHubConfig {
  ssh_key_path: string;
  ssh_public_key: string;
  repos: Record<string, GitHubRepo>;
  auto_push_enabled: boolean;
  departments_with_auto_push: string[];
  last_sync: string | null;
}

export default function GitHubPanel() {
  const [config, setConfig] = useState<GitHubConfig | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const data = await api.getGitHubConfig();
      setConfig(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">加载中...</div>;
  if (!config) return <div className="error">配置加载失败</div>;

  const repos = Object.entries(config.repos || {});

  return (
    <div className="panel github-panel">
      <div className="panel-header"><h2>🔗 GitHub 管理</h2></div>
      
      <div className="section">
        <h3>🔑 SSH 公钥</h3>
        <div className="ssh-key-box"><code>{config.ssh_public_key}</code></div>
        <button onClick={() => navigator.clipboard.writeText(config.ssh_public_key)}>复制</button>
      </div>

      <div className="section">
        <h3>📦 仓库 ({repos.length})</h3>
        {repos.map(([name, repo]: [string, any]) => (
          <div key={name} className="repo-card">
            <strong>{name}</strong>
            <small>{repo.path}</small>
            <small>{repo.branch}</small>
          </div>
        ))}
      </div>
    </div>
  );
}
