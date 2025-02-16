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
    return this.http.get<Team[]>(this.baseURL, )
    .pipe(catchError(error =>{
      console.log("Error fetching teams:", error);
      return throwError(error);
    }))
  }

  addTeam(data : any){
    return this.http.post(`${this.baseURL}`,data,{})
    .pipe(catchError(error =>{
      return throwError(error)
    }))
  }

  getTeam(team_id:number){

    return this.http.get<Team>(`${this.baseURL}${team_id}/`, {})
    .pipe(catchError(error =>{
      return throwError(error);
    }))
  }

  deleteTeam(team_id:number){

    return this.http.delete(`${this.baseURL}${team_id}/`, {})
    .pipe(catchError(error =>{
      return throwError(error);
    }))
  }

  joinTeam(code:number){

    return this.http.get(`${this.baseURL}join/${code}/`)
    .pipe(catchError(error =>{
      return throwError(error);
    }))
  }


  generateAddingLink(teamID : number){
    return this.http.get(`${this.baseURL}${teamID}/addinglink/`)
    .pipe(catchError(error =>{
      return throwError(error);
    }))
  }


  deleteUser(teamID : number, userID : number){
    return this.http.delete(`${this.baseURL}${teamID}/${userID}/`)
    .pipe(catchError(error => {
      return throwError(error);
    }))
  }

  updateTeam(teamID : number, data : any){
    return this.http.patch(`${this.baseURL}${teamID}/`,data)
    .pipe(catchError(error => {
      return throwError(error);
    }))
  }

}
