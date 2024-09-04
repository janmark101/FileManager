import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AuthServiceService } from './auth-service.service';
import { catchError, throwError } from 'rxjs';
import { Response, Folder } from '../Models/Models';



@Injectable({
  providedIn: 'root'
})
export class SiteService {

  constructor(private http: HttpClient,private Auth:AuthServiceService) { }

  baseURL = 'http://localhost:8000/web/';


  getFolders(id:number){
    let headers = this.Auth.setHeaders()

    return this.http.get<Folder[]>(`${this.baseURL}teams/${id}/`, {headers})
    .pipe(catchError(error =>{
      console.log("Error fetching folders: ",error);
      return throwError(error)
    }))
  }

  getSubFoldersFiles(tid:number,fid:number){
    let headers = this.Auth.setHeaders()

    return this.http.get<Response>(`${this.baseURL}teams/${tid}/${fid}`, {headers})
    .pipe(catchError(error =>{
      console.log("Error fetching folders: ",error);
      return throwError(error)
    }))
  }

}
