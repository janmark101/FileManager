import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AuthServiceService } from './auth-service.service';
import { catchError, Subject, throwError } from 'rxjs';
import { Response, Folder } from '../Models/Models';



@Injectable({
  providedIn: 'root'
})
export class SiteService {

  constructor(private http: HttpClient,private Auth:AuthServiceService) { }

  baseURL = 'http://localhost:8000/web/';
  private callNgOnInitSubject = new Subject<void>();
  callNgOnInit$ = this.callNgOnInitSubject.asObservable();

  callNgOnInit() {
    this.callNgOnInitSubject.next();
  }

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

  renameFile(newFileName:string,fileId:number){
    let headers = this.Auth.setHeaders()

    let data = {
      'name' : newFileName
    }

    return this.http.patch(`${this.baseURL}file/${fileId}/`,data,{headers})
    .pipe(catchError(error =>{
      console.log("Error patching file name: ",error);
      return throwError(error)
    }))

  }

  renameFolder(newFileName:string,fileId:number){
    let headers = this.Auth.setHeaders()

    let data = {
      'name' : newFileName
    }

    return this.http.patch(`${this.baseURL}folder/${fileId}/`,data,{headers})
    .pipe(catchError(error =>{
      console.log("Error patching file name: ",error);
      return throwError(error)
    }))

  }

  deleteFile(fileId:number){
    let headers = this.Auth.setHeaders()

    return this.http.delete(`${this.baseURL}file/${fileId}/`,{headers})
    .pipe(catchError(error =>{
      console.log("Error patching file name: ",error);
      return throwError(error)
    }))

  }

  deleteFolder(folderId:number){
    let headers = this.Auth.setHeaders()

    return this.http.delete(`${this.baseURL}folder/${folderId}/`,{headers})
    .pipe(catchError(error =>{
      console.log("Error patching file name: ",error);
      return throwError(error)
    }))

  }

  moveFile(folderId:number,fileId:number){
    let headers = this.Auth.setHeaders() 

    let data = {
      'folder' : folderId
    }

    return this.http.patch(`${this.baseURL}file/${fileId}/`,data,{headers})
    .pipe(catchError(error =>{
      console.log("Error patching file name: ",error);
      return throwError(error)
    }))

  }

  moveFolder(parentFolderId:number,folderId:number){
    let headers = this.Auth.setHeaders() 

    let data = {
      'parent_folder' : parentFolderId
    }

    return this.http.patch(`${this.baseURL}folder/${folderId}/`,data,{headers})
    .pipe(catchError(error =>{
      console.log("Error patching file name: ",error);
      return throwError(error)
    }))

  }


  
  addFolder(folder_name:string, parent_folder_id : number | null, team_id :number){
    let headers = this.Auth.setHeaders()
    let user = this.Auth.getUser()
    
    let data = {
      'team' : team_id,
      'parent_folder' : parent_folder_id,
      'owner' : user.id,
      'name' : folder_name
    }

    return this.http.post(`${this.baseURL}teams/${team_id}/`,data, {headers})
    .pipe(catchError(error =>{
      console.log("Error fetching folders: ",error);
      return throwError(error)
    }))

  }


  addFile(file:FormData, folder_id : number){
    let headers = this.Auth.setHeaders()
  
    return this.http.post(`${this.baseURL}folder/${folder_id}/addfile/`,file, {headers})
    .pipe(catchError(error =>{
      console.log("Error fetching folders: ",error);
      return throwError(error)
    }))

  }

}
