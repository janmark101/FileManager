import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { KeycloakService } from 'keycloak-angular';

@Injectable({
  providedIn: 'root'
})

export class AuthGuard implements CanActivate {
  constructor(private keycloakService: KeycloakService, private router: Router) {}

  canActivate(): boolean {
    if (!( this.keycloakService.isLoggedIn())) {
      this.keycloakService.login({
        redirectUri: window.location.origin + '/' 
      });
      return false;
    }
    return true;
  }
}