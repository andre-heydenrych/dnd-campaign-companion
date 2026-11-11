import { TestBed } from '@angular/core/testing';
import { KnownAccount, KnownAccountsService } from './known-accounts.service';

describe('KnownAccountsService', () => {
  beforeEach(() => localStorage.clear());

  it('moves an account to the top when it logs in again, without duplicating it', () => {
    const accounts = TestBed.inject(KnownAccountsService);
    accounts.remember({ id: 'Frodo', displayName: 'Frodo', kind: 'character' });
    accounts.remember({ id: 'Sam', displayName: 'Sam', kind: 'character' });
    accounts.remember({ id: 'Frodo', displayName: 'Frodo', kind: 'character' });
    expect(accounts.accounts().map((a) => a.id)).toEqual(['Frodo', 'Sam']);
  });

  it('never stores fields other than id, displayName and kind', () => {
    const withExtras = { id: 'Frodo', displayName: 'Frodo', kind: 'character', password: 'x' };
    TestBed.inject(KnownAccountsService).remember(withExtras as KnownAccount);
    expect(localStorage.getItem('knownAccounts')).not.toContain('password');
  });

  it('loads saved accounts and ignores corrupt entries', () => {
    localStorage.setItem(
      'knownAccounts',
      JSON.stringify([{ id: 'Sam', displayName: 'Sam', kind: 'character' }, { id: 1 }, null]),
    );
    expect(TestBed.inject(KnownAccountsService).accounts()).toEqual([
      { id: 'Sam', displayName: 'Sam', kind: 'character' },
    ]);
  });

  it('starts empty if storage holds something that is not JSON', () => {
    localStorage.setItem('knownAccounts', '{oops');
    expect(TestBed.inject(KnownAccountsService).accounts()).toEqual([]);
  });
});
