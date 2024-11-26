import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { catchError } from 'rxjs';
import { User } from '../Models/Models';
import { KeyCloakService } from './key-cloak.service';

@Injectable({
  providedIn: 'root'
})
export class AuthServiceService {


  constructor(private http: HttpClient,private keycloak: KeyCloakService) { 
}


  baseURL = 'http://localhost:8000/auth/';


  setHeaders(){
    let headers = new HttpHeaders();
    
    // let user = this.getUser()

    // if (user && user.token) {
    //   headers = headers.set('Authorization', `Token 42a2e509bb1291503856e8824f8c3299d2824f33`);
    // }
    headers = headers.set('Authorization', `Token 42a2e509bb1291503856e8824f8c3299d2824f33`);

    return headers
  }

  getUser() {
    // const userString = localStorage.getItem('User');
    // return userString ? JSON.parse(userString) : null;
    // this.keycloak.get_user();

  }


  Login(data:any){

    return this.http.post<User>(`${this.baseURL}login/`,data )
      .pipe(catchError(error => {
        console.error('Error while logging in:', error);
        throw error;
      }));
  }



  Logout(){
    let headers = this.setHeaders()
    console.log(headers);
    
    return this.http.post(`${this.baseURL}logout/`,null,{ headers })
      .pipe(catchError(error => {
        console.error('Error while logging out:', error);
        throw error;
      }));
  }

  Register(data:any){
    let headers = this.setHeaders();

    return this.http.post<User>(`${this.baseURL}register/`,data ,{headers})
      .pipe(catchError(error => {
        console.error('Error while logging in:', error);
        throw error;
      }));
  }


  LoginKeyCloak(data:any){

    return this.http.post<User>(`${this.baseURL}keycloaklogin/`,data )
      .pipe(catchError(error => {
        console.error('Error while logging in:', error);
        throw error;
      }));
  }

  RegisterKeyCloak(data:any){
    let headers = this.setHeaders();

    return this.http.post<User>(`${this.baseURL}keycloakregister/`,data ,{headers})
      .pipe(catchError(error => {
        console.error('Error while logging in:', error);
        throw error;
      }));
  }

  deleteAccount(){

  }

  changeData(data : any){
    return this.http.patch(`${this.baseURL}profile/`,data)
    .pipe(catchError(error => {
      console.error('Error while logging in:', error);
      throw error;
    }));
  }
}
