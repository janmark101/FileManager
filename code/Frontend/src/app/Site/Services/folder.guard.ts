import { Injectable } from '@angular/core';
import { ActivatedRoute, CanActivate, Router } from '@angular/router';
import { KeycloakService } from 'keycloak-angular';
import { SiteService } from './site.service';
import { take } from 'rxjs';

@Injectable({
  providedIn: 'root'
})

export class folderGuard implements CanActivate {

  constructor(private siteService: SiteService, private router: Router) {}

  canActivate(): boolean {
    let url = this.router.url.split('/');
    console.log(url);
    
    // this.siteService.checkFolderPermission(Number(url[2]),Number(url.at(-1))).pipe(take(1)).subscribe(data=>{
    //   return true
    // },(error =>{
    //   return true
    // }))
    return true;
  }
}
