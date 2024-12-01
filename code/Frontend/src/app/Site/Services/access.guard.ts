import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { KeycloakService } from 'keycloak-angular';
import { SiteService } from './site.service';
import { catchError, map, Observable, of, take } from 'rxjs';
import { LoginComponent } from '../login/login.component';
import { ToastrService } from 'ngx-toastr';

@Injectable({
  providedIn: 'root'
})

export class accessGuard implements CanActivate {
  constructor(private keycloakService: KeycloakService, private router: Router, private SiteService : SiteService,
    private toast:ToastrService) {}

  canActivate(route: ActivatedRouteSnapshot,state : RouterStateSnapshot): Observable<boolean | UrlTree> {

    let url = state.url.split('/')
  
    
    return this.SiteService.checkResourcePermission(Number(url[2]),url.at(-1),['Default','Part Access','Full Access']).pipe(
      take(1), 
      map((response ) => {
        console.log(response);
        
        if (response) {
          return true;  
        } else {
          return true
        }
      }),
      catchError((error) => {
        this.toast.error(error.error.Error)
        this.router.navigate([''])
        return of(false); 
      })
    );
  }


  
}