import { inject } from '@angular/core';
import { CanActivateFn, Router, Routes } from '@angular/router';
import { Home } from './home/home';
import { Login } from './login/login';
import { UserService } from './user.service';

/** Only let logged-in users through; everyone else goes to the login page. */
const loggedIn: CanActivateFn = () =>
  inject(UserService).username() ? true : inject(Router).parseUrl('/login');

/** Skip the login page if someone is already logged in. */
const loggedOut: CanActivateFn = () =>
  inject(UserService).username() ? inject(Router).parseUrl('/home') : true;

export const routes: Routes = [
  { path: 'login', component: Login, canActivate: [loggedOut] },
  { path: 'home', component: Home, canActivate: [loggedIn] },
  { path: '', pathMatch: 'full', redirectTo: 'login' },
  { path: '**', redirectTo: 'login' },
];
