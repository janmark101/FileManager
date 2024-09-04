import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AuthServiceService } from './auth-service.service';
import { catchError, throwError } from 'rxjs';
import { Team } from '../Models/Models';

@Injectable({
  providedIn: 'root'
})
export class TeamService {

  constructor(private http: HttpClient,private Auth:AuthServiceService) { }

  baseURL = 'http://localhost:8000/auth/teams';


  getTeams(){
    let headers = this.Auth.setHeaders();

    return this.http.get<Team[]>(this.baseURL, {headers})
    .pipe(catchError(error =>{
      console.log("Error fetching teams:", error);
      return throwError(error);
    }))
  }
}
