import { Injectable, inject, signal } from '@angular/core';
import { KnownAccountsService } from './known-accounts.service';

const STORAGE_KEY = 'username';

/**
 * Holds the current username on the client only. There is no password or
 * server check yet; this is a placeholder until real accounts exist.
 * The name is kept in localStorage so a page refresh doesn't log you out.
 */
@Injectable({ providedIn: 'root' })
export class UserService {
  private readonly knownAccounts = inject(KnownAccountsService);
  private readonly _username = signal<string | null>(localStorage.getItem(STORAGE_KEY));
  readonly username = this._username.asReadonly();

  login(username: string): void {
    localStorage.setItem(STORAGE_KEY, username);
    this._username.set(username);
    // For now the username is both the id and the display name.
    this.knownAccounts.remember({ id: username, displayName: username, kind: 'character' });
  }

  /** Ends the session only; the account stays in the remembered list. */
  logout(): void {
    localStorage.removeItem(STORAGE_KEY);
    this._username.set(null);
  }
}
