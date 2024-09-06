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

  baseURL = 'http://localhost:8000/auth/teams/';


  getTeams(){
    let headers = this.Auth.setHeaders();

    return this.http.get<Team[]>(this.baseURL, {headers})
    .pipe(catchError(error =>{
      console.log("Error fetching teams:", error);
      return throwError(error);
    }))
  }

  addTeam(team_name : string){
    let headers = this.Auth.setHeaders()
    let user = this.Auth.getUser()

    let data = {
      "name" : team_name,
      "users" : [],
      "team_owner" : user.id
    }

    return this.http.post(`${this.baseURL}`,data,{headers})
    .pipe(catchError(error =>{
      return throwError(error)
    }))
  }

  getTeam(team_id:number){
    let headers = this.Auth.setHeaders();

    return this.http.get<Team>(`${this.baseURL}${team_id}/`, {headers})
    .pipe(catchError(error =>{
      console.log("Error fetching teams:", error);
      return throwError(error);
    }))
  }

  deleteTeam(team_id:number){
    let headers = this.Auth.setHeaders();

    return this.http.delete(`${this.baseURL}${team_id}/`, {headers})
    .pipe(catchError(error =>{
      console.log("Error deleting team:", error);
      return throwError(error);
    }))
  }

}
