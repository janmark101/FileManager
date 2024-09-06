import { Component, OnInit } from '@angular/core';
import { AuthServiceService } from '../Services/auth-service.service';
import { User } from '../Models/Models';
import { Subscription } from 'rxjs';
import { SiteService } from '../Services/site.service';


@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit{

  user: any;

  subscription: Subscription = new Subscription();
  
  constructor (private Auth:AuthServiceService,private SiteService:SiteService) {}

  ngOnInit(): void {
    this.user = this.Auth.getUser();
    this.subscription = this.SiteService.callNgOnInit$.subscribe(() => {
      this.ngOnInit();
    });

  }



  logout(){
    this.Auth.Logout().subscribe(
      (data: any) => {
        console.log(data)
        localStorage.removeItem('User')
        this.ngOnInit();
        this.SiteService.callNgOnInit();
      },
      error => {
        console.log(error.error)
      }
    );
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }
}
