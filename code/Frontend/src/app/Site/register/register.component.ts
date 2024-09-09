import { Component } from '@angular/core';
import { NgForm } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthServiceService } from '../Services/auth-service.service';
import { ToastrService } from 'ngx-toastr';


@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent {


  constructor(private authService: AuthServiceService,private router: Router,private toast:ToastrService) {}
  error_password:any = []
  error_email:any= []
  error_username:any=[]
  
  ngOnInit(){
    this.error_password = null;
    this.error_email = null;
    this.error_username=null;
  }

  onSubmit(form:NgForm){

    let data ={
      "email": form.value.email,
      "password": form.value.password,
      "first_name": form.value.firstname,
      "last_name": form.value.lastname,
      "username":form.value.username
    }

    this.authService.Register(data).subscribe(
      (response: any) => {
        this.toast.success('Registered Succesfully!','Register')
        form.reset();

      },
      error => {
        console.error('Error:', error.error);

        if (error.error.password){
          this.error_password = error.error.password
        }
        else{
          this.error_password = null
        }
        if (error.error.email){
          this.error_email = error.error.email
        }
        else{
          this.error_email = null
        }
        if (error.error.username){
          this.error_username = error.error.username
        }
        else{
          this.error_username = null
        }

      }
    );
  }

}
