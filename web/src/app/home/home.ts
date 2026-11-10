import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { UserService } from '../user.service';

@Component({
  selector: 'app-home',
  template: `
    <p>Logged in as {{ users.username() }}</p>
    <a href="/login" (click)="logout($event)">Log out</a>
  `,
})
export class Home {
  protected readonly users = inject(UserService);
  private readonly router = inject(Router);

  logout(event: Event): void {
    event.preventDefault();
    this.users.logout();
    this.router.navigateByUrl('/login');
  }
}
