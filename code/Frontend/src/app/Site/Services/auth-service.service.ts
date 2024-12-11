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



  Login(data:any){

    return this.http.post<User>(`${this.baseURL}login/`,data )
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

    return this.http.post<User>(`${this.baseURL}keycloakregister/`,data )
      .pipe(catchError(error => {
        console.error('Error while logging in:', error);
        throw error;
      }));
  }


  changeData(data : any){
    return this.http.patch(`${this.baseURL}profile/`,data)
    .pipe(catchError(error => {
      console.error('Error while logging in:', error);
      throw error;
    }));
  }


  changePassword(data:any){
    return this.http.patch(`${this.baseURL}profile/`,data)
    .pipe(catchError(error => {
      console.error('Error while logging in:', error);
      throw error;
    }));
  }


  createLink(email:any){
    let data = {
      email : email
    }
    return this.http.post(`${this.baseURL}token/`,data)
    .pipe(catchError(error => {
      console.error('Error while logging in:', error);
      throw error;
    }));
  }

}
