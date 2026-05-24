import { getApiBase } from '../apiBase';
import type { GuiUser } from '../types';

const TOKEN_KEY = 'kopano-operator-token';
const USER_KEY = 'kopano-operator-user';

export function readStoredOperator(): { token: string; user: GuiUser } | null {
  const token = window.localStorage.getItem(TOKEN_KEY);
  const rawUser = window.localStorage.getItem(USER_KEY);
  if (!token || !rawUser) {
    return null;
  }
  try {
    return { token, user: JSON.parse(rawUser) as GuiUser };
  } catch {
    return null;
  }
}

export function storeOperator(token: string, user: GuiUser) {
  window.localStorage.setItem(TOKEN_KEY, token);
  window.localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearOperator() {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
}

async function godFetch(path: string, token: string, init?: RequestInit) {
  const headers = new Headers(init?.headers);
  headers.set('Authorization', `Bearer ${token}`);
  if (init?.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  return fetch(`${getApiBase()}${path}`, { ...init, headers });
}

export async function tryDesktopSession(): Promise<{ token: string; user: GuiUser } | null> {
  try {
    const response = await fetch(`${getApiBase()}/api/kc/god/desktop-session`);
    if (!response.ok) {
      return null;
    }
    const data = await response.json();
    if (!data.access_token || !data.user) {
      return null;
    }
    const user = { ...data.user, god_mode: true } as GuiUser;
    storeOperator(data.access_token, user);
    return { token: data.access_token, user };
  } catch {
    return null;
  }
}

export async function loginGod(email: string, password: string) {
  const response = await fetch(`${getApiBase()}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail ?? 'Sign-in failed');
  }
  if (!data.user?.god_mode) {
    throw new Error('This account does not have Super God Mode.');
  }
  storeOperator(data.access_token, data.user);
  return { token: data.access_token as string, user: data.user as GuiUser };
}

export async function fetchGodOverview(token: string) {
  const response = await godFetch('/api/kc/god/overview', token);
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function runGodAction(token: string, action: string, confirm = false) {
  const response = await godFetch('/api/kc/god/actions/run', token, {
    method: 'POST',
    body: JSON.stringify({ action, confirm }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail ?? 'Action failed');
  }
  return data;
}

export async function runGodGit(token: string, action: string, confirm = false) {
  const response = await godFetch('/api/kc/god/git/run', token, {
    method: 'POST',
    body: JSON.stringify({ action, confirm }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail ?? 'Git action failed');
  }
  return data;
}
