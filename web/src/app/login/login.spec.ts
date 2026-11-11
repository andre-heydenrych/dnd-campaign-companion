import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { Login } from './login';
import { KnownAccountsService } from '../known-accounts.service';
import { UserService } from '../user.service';

describe('Login', () => {
  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({ providers: [provideRouter([])] });
  });

  async function render() {
    const fixture = TestBed.createComponent(Login);
    await fixture.whenStable();
    return { fixture, el: fixture.nativeElement as HTMLElement };
  }

  function typeAndSubmit(el: HTMLElement, value: string) {
    const input = el.querySelector('input')!;
    input.value = value;
    input.dispatchEvent(new Event('input'));
    el.querySelector('form')!.dispatchEvent(new Event('submit'));
  }

  it('stores the trimmed username and goes to /home on submit', async () => {
    const navigate = vi.spyOn(TestBed.inject(Router), 'navigateByUrl').mockResolvedValue(true);
    const { el } = await render();

    typeAndSubmit(el, '  Aragorn ');

    expect(TestBed.inject(UserService).username()).toBe('Aragorn');
    expect(navigate).toHaveBeenCalledWith('/home');
  });

  it('disables the button while the username is blank', async () => {
    const { el } = await render();
    expect(el.querySelector<HTMLButtonElement>('form button')!.disabled).toBe(true);
  });

  it('shows no remembered accounts when there are none', async () => {
    const { el } = await render();
    expect(el.querySelector('.known-accounts')).toBeNull();
  });

  it('remembers the account after a successful login', async () => {
    vi.spyOn(TestBed.inject(Router), 'navigateByUrl').mockResolvedValue(true);
    const { el } = await render();

    typeAndSubmit(el, 'Aragorn');

    const expected = [{ id: 'Aragorn', displayName: 'Aragorn', kind: 'character' }];
    expect(TestBed.inject(KnownAccountsService).accounts()).toEqual(expected);
    // Only these three fields are written; no password or code.
    expect(JSON.parse(localStorage.getItem('knownAccounts')!)).toEqual(expected);
  });

  it('continues as a remembered account in one click', async () => {
    const accounts = TestBed.inject(KnownAccountsService);
    accounts.remember({ id: 'Legolas', displayName: 'Legolas', kind: 'character' });
    accounts.remember({ id: 'Gimli', displayName: 'Gimli', kind: 'character' });
    const navigate = vi.spyOn(TestBed.inject(Router), 'navigateByUrl').mockResolvedValue(true);
    const { el } = await render();

    const buttons = [...el.querySelectorAll<HTMLButtonElement>('button.continue')];
    expect(buttons.map((b) => b.textContent!.trim())).toEqual([
      'Continue as Gimli',
      'Continue as Legolas',
    ]);
    // The remembered accounts sit above the normal username form.
    expect(el.querySelector('.known-accounts + form')).not.toBeNull();

    buttons[1].click();

    expect(TestBed.inject(UserService).username()).toBe('Legolas');
    expect(navigate).toHaveBeenCalledWith('/home');
  });

  it('forgets a remembered account without logging in', async () => {
    const accounts = TestBed.inject(KnownAccountsService);
    accounts.remember({ id: 'Legolas', displayName: 'Legolas', kind: 'character' });
    accounts.remember({ id: 'Gimli', displayName: 'Gimli', kind: 'character' });
    const navigate = vi.spyOn(TestBed.inject(Router), 'navigateByUrl').mockResolvedValue(true);
    const { fixture, el } = await render();

    el.querySelector<HTMLButtonElement>('button[aria-label="Forget Gimli"]')!.click();
    await fixture.whenStable();

    expect(accounts.accounts().map((a) => a.id)).toEqual(['Legolas']);
    expect(JSON.parse(localStorage.getItem('knownAccounts')!)).toHaveLength(1);
    expect(el.textContent).not.toContain('Continue as Gimli');
    expect(el.textContent).toContain('Continue as Legolas');
    expect(TestBed.inject(UserService).username()).toBeNull();
    expect(navigate).not.toHaveBeenCalled();
  });
});
