import { Component, OnInit } from '@angular/core';
import { AuthServiceService } from '../Services/auth-service.service';
import { User } from '../Models/Models';
import { Subscription } from 'rxjs';
import { SiteService } from '../Services/site.service';
import { KeyCloakService } from '../Services/key-cloak.service';
import { KeycloakService } from 'keycloak-angular';
import { Router } from '@angular/router';


@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit{

  user: boolean = false;
  userinfo:any;

  subscription: Subscription = new Subscription();
  
  constructor (private keycloak:KeyCloakService,private SiteService:SiteService,private keycloaksService:KeycloakService,private router:Router) {}

  ngOnInit(): void {
    this.user = this.keycloak.Logged();
    this.get_user();    
    
  }

  get_user() {
    if (this.user == true){
      this.keycloaksService.loadUserProfile().then(userInfo => {
        this.userinfo = userInfo
        
      }).catch(error => {
        console.error("Błąd podczas ładowania profilu użytkownika", error);
      });
    }
    else{
      this.userinfo = undefined;
    }

  }

  login(){
    this.keycloak.Login();
  }

  logout(){
    this.keycloak.Logout();
  }

}
