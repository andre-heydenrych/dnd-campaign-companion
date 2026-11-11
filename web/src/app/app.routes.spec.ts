import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { RouterTestingHarness } from '@angular/router/testing';
import { routes } from './app.routes';
import { UserService } from './user.service';

describe('route guards', () => {
  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({ providers: [provideRouter(routes)] });
  });

  it('sends a logged-out visitor from /home to /login, even with remembered accounts', async () => {
    const users = TestBed.inject(UserService);
    users.login('Gimli');
    users.logout();
    const harness = await RouterTestingHarness.create();
    await harness.navigateByUrl('/home');
    expect(TestBed.inject(Router).url).toBe('/login');
  });

  it('sends a logged-in user from /login to /home', async () => {
    TestBed.inject(UserService).login('Gimli');
    const harness = await RouterTestingHarness.create();
    await harness.navigateByUrl('/login');
    expect(TestBed.inject(Router).url).toBe('/home');
  });
});
