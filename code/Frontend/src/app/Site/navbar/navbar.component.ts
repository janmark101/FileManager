import { Component, OnInit } from '@angular/core';
import { AuthServiceService } from '../Services/auth-service.service';
import { User } from '../Models/Models';


@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit{

  user: any;


  constructor (private Auth:AuthServiceService) {}

  ngOnInit(): void {
    this.user = this.Auth.getUser();
    
  }

  login(){

    let data = {
      "username" : 'jmark',
      "password" : "123"
    }

    this.Auth.Login(data).subscribe(
      (data: any) => {
        console.log(data)
        localStorage.setItem('User', JSON.stringify(data.user))
        this.ngOnInit();
      },
      error => {
        console.log(error.error)
      }
    );
  }

  logout(){
    this.Auth.Logout().subscribe(
      (data: any) => {
        console.log(data)
        localStorage.removeItem('User')
        this.ngOnInit();
      },
      error => {
        console.log(error.error)
      }
    );
  }
}
