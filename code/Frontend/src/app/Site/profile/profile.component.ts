import { Component, OnInit } from '@angular/core';
import { ConfirmBoxEvokeService } from '@costlydeveloper/ngx-awesome-popup';
import { ToastrService } from 'ngx-toastr';
import { AuthServiceService } from '../Services/auth-service.service';
import { take } from 'rxjs';
import { KeyCloakService } from '../Services/key-cloak.service';
import { KeycloakService } from 'keycloak-angular';
import emailjs from 'emailjs-com';
import { NgForm } from '@angular/forms';


@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit{


  constructor(private toast : ToastrService, private confirmBoxEvokeService: ConfirmBoxEvokeService, private Auth: AuthServiceService,
    private keycloak:KeyCloakService, private keycloaksService:KeycloakService
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
    deleteAccount: false
  };

  // user: boolean = false;

  ngOnInit(): void {
    // this.user = this.keycloak.Logged();  
    this.get_user(); 
  }

  get_user() {
    if (true){
      this.keycloaksService.loadUserProfile().then(userInfo => {
        console.log(userInfo.firstName);
        this.user.firstName = userInfo.firstName as string;
        this.user.lastName = userInfo.lastName as string;
        this.user.email = userInfo.email as string;
        this.user.username = userInfo.username as string;
        
      }).catch(error => {
        console.error("Błąd podczas ładowania profilu użytkownika", error);
      });
    }
    else{
      // this.userinfo = undefined;
    }

  }



  toggleSection(section: string) {    
    this.sections[section] = !this.sections[section];
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
      // tu trzeba jakby wymusisc wyslanie nowego tokenu bo jak tego nie zrobie to dopoki nie odswieze strony to get_user() zwroci 
      // stary firstname i lastname (nawet jak zmienie komponenty)
    }),error=>{
      console.log("problemy");
      
    })
  }

  onSubmitPassword() {
    // Logika zmiany hasła
    console.log('Nowe hasło:', this.user.password);
  }

  onSubmitEmail(form : NgForm) {
    const templateParams = {
      user_email: form.value['email'],
      message: 'Your email change confirmation link...',
      Subject : "Email change",
      to_name : this.user.firstName + " " + this.user.lastName,
      send_to : this.user.email
    };
    
    
    emailjs.send('service_bv2thlp', 'template_6lcbf4c', templateParams, 'VO4iyOWz6JYto-Q_s')
    .then((response) => {
      console.log('Email sent successfully', response);
    })
    .catch((error) => {
      console.error('Error sending email', error);
    });
  }

  deleteAccount() {
    const templateParams = {
      message: 'Your email change confirmation link...',
      Subject : "Email change",
      to_name : this.user.firstName + " " + this.user.lastName,
      send_to : this.user.email
    };


    // this.confirmBoxEvokeService.danger('Confirm delete!', 'Are you sure you want to delete it?', 'Confirm', 'Decline')
    // .subscribe(resp => {
    //   this.Auth.deleteAccount().pipe(take(1)).subscribe((data =>{
        
    //   }), error =>{

    //   })
    // });
  }


}
