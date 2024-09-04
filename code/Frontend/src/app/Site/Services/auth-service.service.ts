import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { catchError } from 'rxjs';
import { User } from '../Models/Models';

@Injectable({
  providedIn: 'root'
})
export class AuthServiceService {

  constructor(private http: HttpClient) { }

  baseURL = 'http://localhost:8000/auth/';


  setHeaders(){
    let headers = new HttpHeaders();
    
    let user = this.getUser()

    if (user && user.token) {
      headers = headers.set('Authorization', `Token ${user.token}`);
    }

    return headers
  }

  getUser() {
    const userString = localStorage.getItem('User');
    return userString ? JSON.parse(userString) : null;
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
}
