import { Component, inject } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { KnownAccount, KnownAccountsService } from '../known-accounts.service';
import { UserService } from '../user.service';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule],
  template: `
    <h1>Log in</h1>
    @if (knownAccounts.accounts().length) {
      <ul class="known-accounts">
        @for (account of knownAccounts.accounts(); track account.id) {
          <li>
            <button type="button" class="continue" (click)="continueAs(account)">
              Continue as {{ account.displayName }}
            </button>
            <button
              type="button"
              class="forget"
              [attr.aria-label]="'Forget ' + account.displayName"
              (click)="knownAccounts.forget(account.id)"
            >
              forget
            </button>
          </li>
        }
      </ul>
    }
    <form [formGroup]="form" (ngSubmit)="submit()">
      <label for="username">Username</label>
      <input id="username" formControlName="username" autocomplete="username" autofocus />
      <button type="submit" [disabled]="form.invalid">Log in</button>
    </form>
  `,
  styles: `
    .known-accounts {
      list-style: none;
      padding: 0;
    }
    .forget {
      font-size: 0.8em;
      margin-left: 0.5em;
    }
  `,
})
export class Login {
  private readonly users = inject(UserService);
  private readonly router = inject(Router);
  protected readonly knownAccounts = inject(KnownAccountsService);

  protected readonly form = new FormGroup({
    username: new FormControl('', {
      nonNullable: true,
      // \S: must contain at least one non-space character
      validators: [Validators.required, Validators.pattern(/\S/)],
    }),
  });

  submit(): void {
    const name = this.form.controls.username.value.trim();
    if (!name) return;
    this.users.login(name);
    this.router.navigateByUrl('/home');
  }

  continueAs(account: KnownAccount): void {
    this.users.login(account.id);
    this.router.navigateByUrl('/home');
  }
}
