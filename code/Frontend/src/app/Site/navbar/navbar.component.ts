import { Component, OnInit } from '@angular/core';
import { AuthServiceService } from '../Services/auth-service.service';
import { User } from '../Models/Models';
import { Subscription } from 'rxjs';
import { SiteService } from '../Services/site.service';
import { KeyCloakService } from '../Services/key-cloak.service';
import { KeycloakService } from 'keycloak-angular';


@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit{

  user: any;

  subscription: Subscription = new Subscription();
  
  constructor (private keycloak:KeyCloakService,private SiteService:SiteService,private keycloaksService:KeycloakService) {}

  ngOnInit(): void {
    this.user = this.keycloak.Logged();
    console.log(this.user)
    console.log(this.keycloaksService.getKeycloakInstance().resourceAccess?.['angular-app']?.roles || [],'roles ');
    // this.subscription = this.SiteService.callNgOnInit$.subscribe(() => {
    //   this.ngOnInit();
    // });

  }

  login(){
    this.keycloak.Login();
  }

  logout(){
    this.keycloak.Logout();
  }

  // ngOnDestroy(): void {
  //   this.subscription.unsubscribe();
  // }
}
