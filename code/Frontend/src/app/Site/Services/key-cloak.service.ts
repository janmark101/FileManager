import { Injectable } from '@angular/core';
import { KeycloakService } from 'keycloak-angular';

@Injectable({
  providedIn: 'root'
})
export class KeyCloakService {

  constructor(private keycloakService : KeycloakService) { }


  Login(){
    this.keycloakService.login();
  }

  Logout(){
    this.keycloakService.logout();
  }

  Logged(){
    return this.keycloakService.isLoggedIn();
  }

}
