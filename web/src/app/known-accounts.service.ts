import { Injectable, signal } from '@angular/core';

const STORAGE_KEY = 'knownAccounts';

export type AccountKind = 'character' | 'campaign';

/**
 * An account this browser has logged in as before. Only these three fields
 * are ever stored: never a password or code.
 */
export interface KnownAccount {
  id: string;
  displayName: string;
  kind: AccountKind;
}

/**
 * Remembers accounts that have logged in on this browser, newest first, so the
 * login page can offer "Continue as ...". Kept in localStorage, separate from
 * the current session, so logging out does not forget them.
 */
@Injectable({ providedIn: 'root' })
export class KnownAccountsService {
  private readonly _accounts = signal<KnownAccount[]>(load());
  readonly accounts = this._accounts.asReadonly();

  /** Add an account, or move it to the top if it is already known. */
  remember(account: KnownAccount): void {
    // Copy only the allowed fields, so nothing else can sneak into storage.
    const { id, displayName, kind } = account;
    this.save([{ id, displayName, kind }, ...this._accounts().filter((a) => a.id !== id)]);
  }

  forget(id: string): void {
    this.save(this._accounts().filter((a) => a.id !== id));
  }

  private save(accounts: KnownAccount[]): void {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(accounts));
    this._accounts.set(accounts);
  }
}

/** Read the list from storage, dropping anything that isn't a valid account. */
function load(): KnownAccount[] {
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]');
    return Array.isArray(parsed) ? parsed.filter(isKnownAccount) : [];
  } catch {
    return [];
  }
}

function isKnownAccount(value: unknown): value is KnownAccount {
  const a = value as Partial<KnownAccount> | null;
  return (
    typeof a?.id === 'string' &&
    typeof a.displayName === 'string' &&
    (a.kind === 'character' || a.kind === 'campaign')
  );
}
