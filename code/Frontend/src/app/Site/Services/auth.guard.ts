import { CanActivate, Router } from '@angular/router';
import { KeycloakService } from 'keycloak-angular';

export class AuthGuard implements CanActivate {
  constructor(private keycloakService: KeycloakService, private router: Router) {}

  async canActivate(): Promise<boolean> {
    if (!(await this.keycloakService.isLoggedIn())) {
      this.router.navigate(['/login']);
      return false;
    }
    return true;
  }
}