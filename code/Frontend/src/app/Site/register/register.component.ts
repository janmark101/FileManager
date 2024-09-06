import { Component } from '@angular/core';
import { NgForm } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthServiceService } from '../Services/auth-service.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent {


  constructor(private authService: AuthServiceService,private router: Router) {}
  error_password:any = []
  error_email:any= []
  
  ngOnInit(){
    this.error_password = null;
    this.error_email = null;
  }

  onSubmit(form:NgForm){


    let data ={
      "email": form.value.email,
      "password": form.value.password,
      "firstname": form.value.firstname,
      "lastname": form.value.lastname
    }

    // this.authService.register(data).subscribe(
    //   (response: any) => {
    //     this.toast.success("Zarejestrowano pomyślnie",'Rejestracja')
    //     this.router.navigate(['profile']);

    //   },
    //   error => {
    //     console.error('Error:', error.error);

    //     if (error.error.password){
    //       this.error_password = error.error.password
    //     }
    //     else{
    //       this.error_password = null
    //     }
    //     if (error.error.email){
    //       this.error_email = error.error.email
    //     }
    //     else{
    //       this.error_email = null
    //     }

    //   }
    // );
  }

}
