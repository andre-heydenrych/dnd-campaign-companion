import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { Home } from './home';
import { UserService } from '../user.service';

describe('Home', () => {
  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({ providers: [provideRouter([])] });
    TestBed.inject(UserService).login('Gimli');
  });

  it('shows who is logged in', async () => {
    const fixture = TestBed.createComponent(Home);
    await fixture.whenStable();
    expect((fixture.nativeElement as HTMLElement).textContent).toContain('Logged in as Gimli');
  });

  it('logs out and goes to /login', async () => {
    const navigate = vi.spyOn(TestBed.inject(Router), 'navigateByUrl').mockResolvedValue(true);
    const fixture = TestBed.createComponent(Home);
    await fixture.whenStable();
    (fixture.nativeElement as HTMLElement).querySelector('a')!.click();
    expect(TestBed.inject(UserService).username()).toBeNull();
    expect(navigate).toHaveBeenCalledWith('/login');
  });
});
