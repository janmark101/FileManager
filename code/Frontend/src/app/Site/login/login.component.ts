import { Component } from '@angular/core';
import { NgForm } from '@angular/forms';
import { User } from '../Models/Models';
import { AuthServiceService } from '../Services/auth-service.service';
import { Router } from '@angular/router';
import { SiteService } from '../Services/site.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {


  
  constructor(private Auth : AuthServiceService,private router: Router, private SiteService:SiteService){};

  
  error:string|null = null


  onSubmit(form: NgForm){

    let data = {
      "username" : form.value['username'],
      "password" : form.value['password']
    }

    if (data['username'].length == 0 || data['password'] ==0){
      this.error = 'Dont leave empty fields!';
      return
    }
    

    this.Auth.Login(data).subscribe(
      (data: any) => {
        console.log(data)
        localStorage.setItem('User', JSON.stringify(data.user))
        this.SiteService.callNgOnInit();
        this.router.navigate([''])
      },
      error => {        
        this.error=error.error.error
      }
    );
  }

}
