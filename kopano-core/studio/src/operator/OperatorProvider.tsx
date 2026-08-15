import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import type { GuiUser } from '../types';
import {
  clearOperator,
  fetchGodOverview,
  loginGod,
  readStoredOperator,
  runGodAction,
  runGodGit,
  tryDesktopSession,
} from './operatorApi';

interface GodOverview {
  persona_route?: string;
  proof_bar_pass?: boolean;
  git?: { branch?: string; head_sha?: string; ahead?: number; behind?: number };
  cassy?: { display_name?: string; mission?: string };
}

interface OperatorContextValue {
  token: string | null;
  user: GuiUser | null;
  isGodMode: boolean;
  overview: GodOverview | null;
  lastOutput: string;
  busy: boolean;
  error: string | null;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => void;
  refreshOverview: () => Promise<void>;
  runAction: (action: string, confirm?: boolean) => Promise<void>;
  runGit: (action: string, confirm?: boolean) => Promise<void>;
}

const OperatorContext = createContext<OperatorContextValue | null>(null);

export function OperatorProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<GuiUser | null>(null);
  const [overview, setOverview] = useState<GodOverview | null>(null);
  const [lastOutput, setLastOutput] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const applySession = useCallback((session: { token: string; user: GuiUser }) => {
    setToken(session.token);
    setUser(session.user);
    setError(null);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const boot = async () => {
      const stored = readStoredOperator();
      if (stored?.user.god_mode) {
        if (!cancelled) {
          applySession(stored);
        }
        return;
      }
      const desktop = await tryDesktopSession();
      if (!cancelled && desktop) {
        applySession(desktop);
      }
    };
    void boot();
    return () => {
      cancelled = true;
    };
  }, [applySession]);

  const refreshOverview = useCallback(async () => {
    if (!token) {
      return;
    }
    const data = await fetchGodOverview(token);
    setOverview(data);
  }, [token]);

  useEffect(() => {
    if (!token) {
      return;
    }
    void refreshOverview().catch((err: unknown) => {
      setError(err instanceof Error ? err.message : 'Overview failed');
    });
  }, [token, refreshOverview]);

  const signIn = useCallback(async (email: string, password: string) => {
    setBusy(true);
    setError(null);
    try {
      const session = await loginGod(email, password);
      applySession(session);
      await refreshOverview();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Sign-in failed');
      throw err;
    } finally {
      setBusy(false);
    }
  }, [applySession, refreshOverview]);

  const signOut = useCallback(() => {
    clearOperator();
    setToken(null);
    setUser(null);
    setOverview(null);
    setLastOutput('');
    setError(null);
  }, []);

  const runAction = useCallback(async (action: string, confirm = false) => {
    if (!token) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const result = await runGodAction(token, action, confirm);
      setLastOutput(result.tail ?? JSON.stringify(result, null, 2));
      await refreshOverview();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Action failed');
    } finally {
      setBusy(false);
    }
  }, [token, refreshOverview]);

  const runGit = useCallback(async (action: string, confirm = false) => {
    if (!token) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const result = await runGodGit(token, action, confirm);
      setLastOutput(result.output ?? JSON.stringify(result, null, 2));
      await refreshOverview();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Git failed');
    } finally {
      setBusy(false);
    }
  }, [token, refreshOverview]);

  const value = useMemo<OperatorContextValue>(
    () => ({
      token,
      user,
      isGodMode: Boolean(user?.god_mode),
      overview,
      lastOutput,
      busy,
      error,
      signIn,
      signOut,
      refreshOverview,
      runAction,
      runGit,
    }),
    [token, user, overview, lastOutput, busy, error, signIn, signOut, refreshOverview, runAction, runGit],
  );

  return <OperatorContext.Provider value={value}>{children}</OperatorContext.Provider>;
}

// The provider and its hook intentionally share one module API. This is the only
// non-component export in the file and does not affect Fast Refresh state.
// eslint-disable-next-line react-refresh/only-export-components
export function useOperator() {
  const ctx = useContext(OperatorContext);
  if (!ctx) {
    throw new Error('useOperator must be used within OperatorProvider');
  }
  return ctx;
}
