import { Component, OnInit } from '@angular/core';
import { ConfirmBoxEvokeService } from '@costlydeveloper/ngx-awesome-popup';
import { ToastrService } from 'ngx-toastr';
import { AuthServiceService } from '../Services/auth-service.service';
import { take } from 'rxjs';
import { KeyCloakService } from '../Services/key-cloak.service';
import { KeycloakService } from 'keycloak-angular';
import emailjs from 'emailjs-com';
import { NgForm } from '@angular/forms';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';


@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit{


  constructor(private toast : ToastrService, private confirmBoxEvokeService: ConfirmBoxEvokeService, private Auth: AuthServiceService,
    private keycloak:KeyCloakService, private keycloaksService:KeycloakService, private router : Router
  ){}

  user = {
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    username : ''
  };

  sections: {
    [key: string]: boolean;
  } = {
    personalData: false,
    email: false,
    password: false,
  };

  passwordError : string = "";

  ngOnInit(): void {
    this.get_user(); 
  }

  get_user() {
    this.keycloaksService.loadUserProfile().then(userInfo => {
      this.user.firstName = userInfo.firstName as string;
      this.user.lastName = userInfo.lastName as string;
      this.user.email = userInfo.email as string;
      this.user.username = userInfo.username as string;
    }).catch(error => {
      this.router.navigate([''])
    });
  }



  toggleSection(section: string) {    
    this.sections[section] = !this.sections[section];
    this.passwordError = "";
  }

  onSubmitPersonalData(form : NgForm) {
    
    let data = {
      payload : {
        "firstName" : form.value['firstName'],
        "lastName" : form.value['lastName']
        } 
    }

    this.Auth.changeData(data).pipe(take(1)).subscribe((response =>{
      this.user.firstName = data.payload.firstName
      this.user.lastName = data.payload.lastName
      this.sections['personalData'] = false;
      this.toast.success("Personal data changed!")
      location.reload()
    }),error=>{
      console.log("problemy");
      
    })
  }

  onSubmitPassword(form : NgForm) {
    const passwordRegex = /^(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[A-Z])[A-Za-z\d!@#$%^&*]{8,}$/;
    
    if( form.value['password'] != form.value['confirm_password'])
    {
      this.passwordError = "Passwords do not match. Please try again."
      return
    }

    if(!passwordRegex.test(form.value['password'])){
      this.passwordError = "Password does not meet the criteria!";
      return
    }


    console.log(form.value['password']);
    
    let data = {
      payload : {
        "password" : form.value['password'],
        } ,
      hash : form.value['old_password']
    }

    this.Auth.changePassword(data).pipe(take(1)).subscribe((data =>{
      this.keycloak.Logout()
      
    }), error =>{
      console.log(error);
      
    })

  }

  onSubmitEmail(form : NgForm) {
    const templateParams = {
      user_email: form.value['email'],
      message: 'Your email change confirmation link : ',
      Subject : "Email change",
      to_name : this.user.firstName + " " + this.user.lastName,
      send_to : this.user.email, 
      link : ""
    };

    this.Auth.createLink(form.value['email']).pipe(take(1)).subscribe((data=>{
      templateParams['link'] = "http://localhost:4200/email/" + data
      emailjs.send('service_bv2thlp', 'template_6lcbf4c', templateParams, 'VO4iyOWz6JYto-Q_s')
      .then((response) => {
        this.toast.info("Verification email sent succesfully.")
        form.reset();
      })
      .catch((error) => {
        this.toast.error('Something went wrong!')
      });
      
    }), error =>{
      this.toast.error("Something went wrong!")
    })
    
  }




}
