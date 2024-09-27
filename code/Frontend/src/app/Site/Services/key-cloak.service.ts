import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { KeycloakService } from 'keycloak-angular';

@Injectable({
  providedIn: 'root'
})
export class KeyCloakService {

  constructor(private keycloakService : KeycloakService,private router:Router) { }


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
