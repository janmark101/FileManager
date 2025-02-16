import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { AuthServiceService } from './auth-service.service';
import { catchError, Subject, throwError } from 'rxjs';
import { Response, Resource, ResourcePermissions } from '../Models/Models';



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

  getResources(id:number){
    return this.http.get<Resource[]>(`${this.baseURL}teams/${id}/`)
    .pipe(catchError(error =>{
      return throwError(error)
    }))
  }

  getSubResourcesFiles(tid:number,fid:unknown){
    return this.http.get<Response>(`${this.baseURL}teams/${tid}/${fid}/`)
    .pipe(catchError(error =>{
      return throwError(error)
    }))
  }

  renameFile(newFileName:string, fileID : number | string){
    let data = {
      'name' : newFileName
    }

    return this.http.patch(`${this.baseURL}file/${fileID}/`,data,)
    .pipe(catchError(error =>{
      return throwError(error)
    }))
  }

  renameResource(newFileName:string,fileId:string, team_id : number){
    let data = {
      'name' : newFileName
    }

    return this.http.patch(`${this.baseURL}resource/${fileId}/${team_id}/`,data)
    .pipe(catchError(error =>{
      return throwError(error)
    }))
  }

  deleteFile(fileId:number){
    return this.http.delete(`${this.baseURL}file/${fileId}/`)
    .pipe(catchError(error =>{
      return throwError(error)
    }))
  }

  deleteResource(resourceID:string, team_id : number){
    return this.http.delete(`${this.baseURL}resource/${resourceID}/${team_id}/`)
    .pipe(catchError(error =>{
      return throwError(error)
    }))
  }

  moveFile(folderId:number | string,fileId:number | any){
    let data = {
      'resource' : folderId
    }

    return this.http.patch(`${this.baseURL}file/${fileId}/`,data)
    .pipe(catchError(error =>{
      return throwError(error)
    }))
  }

  moveResource(parentResourceID : string,resourceID : string, team_id : number){
    let data = {
      'parent_resource' : parentResourceID
    }

    return this.http.patch(`${this.baseURL}resource/${resourceID}/${team_id}/`,data)
    .pipe(catchError(error =>{
      console.log("Error patching file name: ",error);
      return throwError(error)
    }))
  }


  
  addResource(resourceName : string, parentResourceID : string | unknown, teamID :number,scope:string){
    let data = {
      'team' : teamID,
      'parent_resource' : parentResourceID,
      'scope' : scope,
      'name' : resourceName
    }

    return this.http.post(`${this.baseURL}teams/${teamID}/`,data)
  }


  addFile(file:FormData, resourceID : string){  
    return this.http.post(`${this.baseURL}resource/${resourceID}/addfile/`,file)
    .pipe(catchError(error =>{
      return throwError(error)
    }))
  }


  checkResourcePermission(teamID : number, resourceID : unknown, scopes : unknown){
    let data = {
      "scopes" : scopes
    }

    return this.http.post(`${this.baseURL}resource/${teamID}/${resourceID}/permission`,data)
    .pipe(catchError(error =>{
      return throwError(error)
    }))
  }


  getPermissions(teamID : number, resourceID : string){
    return this.http.get<ResourcePermissions>(`${this.baseURL}resource/${teamID}/${resourceID}/permissions`)
    .pipe(catchError(error =>{
      return throwError(error)
    }))
  }

  changeResourcePermissions(teamID : number,resourceID : string, permissions : any[]){
    let data = {
      "permissions" : permissions
    }

    return this.http.post(`${this.baseURL}resource/${teamID}/${resourceID}/permissions`, data)
    .pipe(catchError(error =>{
      return throwError(error)
    }))
  }

  downloadFile(id : number){
    return this.http.get(`${this.baseURL}download/${id}/`, { responseType: 'blob' });
  }

}
