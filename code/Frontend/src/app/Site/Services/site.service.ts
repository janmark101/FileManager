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


    return this.http.get<Folder[]>(`${this.baseURL}teams/${id}/`)
    .pipe(catchError(error =>{
      console.log("Error fetching folders: ",error);
      return throwError(error)
    }))
  }

  getSubFoldersFiles(tid:number,fid:unknown){

    return this.http.get<Response>(`${this.baseURL}teams/${tid}/${fid}/`)
    .pipe(catchError(error =>{
      console.log("Error fetching folders: ",error);
      return throwError(error)
    }))
  }

  renameFile(newFileName:string,fileId:number){
  

    let data = {
      'name' : newFileName
    }

    return this.http.patch(`${this.baseURL}file/${fileId}/`,data,)
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


  
  addFolder(folder_name:string, parent_folder_id : string | unknown, team_id :number,scope:string){
    
    let data = {
      'team' : team_id,
      'parent_folder' : parent_folder_id,
      'scope' : scope,
      'name' : folder_name
    }

    return this.http.post(`${this.baseURL}teams/${team_id}/`,data)
    .pipe(catchError(error =>{
      console.log("Error fetching folders: ",error);
      return throwError(error)
    }))

  }


  addFile(file:FormData, folder_id : string | unknown){
    let headers = this.Auth.setHeaders()
  
    return this.http.post(`${this.baseURL}folder/${folder_id}/addfile/`,file, {headers})
    .pipe(catchError(error =>{
      console.log("Error fetching folders: ",error);
      return throwError(error)
    }))

  }


  checkFolderPermission(tid:number,fid:number,scopes:unknown){
    let data = {
      "scopes" : scopes
    }
    return this.http.post(`${this.baseURL}folder/${tid}/${fid}/permission`,data)
    .pipe(catchError(error =>{
      console.log("Error: ",error);
      return throwError(error)
    }))
  }
}
