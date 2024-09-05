import { Component, HostListener } from '@angular/core';
import { take } from 'rxjs';
import { Team, File_,Folder, Response } from '../Models/Models';
import { ActivatedRoute, Router } from '@angular/router';
import { SiteService } from '../Services/site.service';
import { NgForm } from '@angular/forms';
import {
  ConfirmBoxEvokeService,
  
} from '@costlydeveloper/ngx-awesome-popup';



@Component({
  selector: 'app-sub-folder',
  templateUrl: './sub-folder.component.html',
  styleUrls: ['./sub-folder.component.scss']
})
export class SubFolderComponent {

  Folders : Folder[] = []
  Files : File_[] = []
  accTeam : Team = {
    id : 0,
    name : "",
    "users" : [],
    created_at :  new Date(),
    user : 0
  }

  extIcons = ['csv','docx','exe','jpg','json','mp4','pdf','png','ppt','xml','js','txt','html','mp3','zip','ppt']

  path : string[] = []
  path_ids : string[] = []

  currentPath: string[] = [];
 
  constructor(private SiteService:SiteService, private route:ActivatedRoute, private router: Router,private confirmBoxEvokeService: ConfirmBoxEvokeService) {}

  ngOnInit(): void {
    this.Folders = []
    this.Files  = []
    this.currentPath = [];
    this.path = [];
    this.path_ids = [];
    this.fetchSubFoldersFiles();
  }

  buildPath(initialId: string): string[] {

    return [initialId];
  }

  fetchSubFoldersFiles(){
    this.currentPath = this.router.url.split('/');
    
    this.SiteService.getSubFoldersFiles(Number(this.currentPath[2]),Number(this.currentPath.at(-1))).pipe(take(1)).subscribe((data:Response) =>{
      
      this.Folders = data.folders;
      this.accTeam = data.team;
      this.Files = data.files;
      console.log(data);
      
      this.path = data.folder_names_ids[0];
      this.path_ids = data.folder_names_ids[1]
      console.log(data);
      
      this.makePath();
      
    },(error:any) =>{
      console.error(error);
      
    })
  }

  makePath(){
    this.path.unshift(this.accTeam.name)
    
  }

  navigateToSubfolder(folderId: number): void {
    let url = this.router.url + "/" + folderId
    this.router.navigateByUrl(url).then(()=>{
      this.ngOnInit();
    })
  }

  navigateToUrl(folderId:string){
    let index = this.path.indexOf(folderId)
    let temp = this.currentPath.slice(1,index+3)

    let url = 'teams'
    
    for (let index = 1; index < temp.length; index++) {
      url +=  '/' +  temp[index] 
    }
    
    this.router.navigateByUrl(url).then(()=>{
      this.ngOnInit();
    })
  }


  getIconUrl(file: any): string {
    const fileExtension = file.name.split('.').pop();
    
    if (this.extIcons.includes(fileExtension))
      return `assets/WebImages/icons/${fileExtension}.png`
    else
      return `assets/WebImages/icons/file.png`
    }

    isDropdownOpen: boolean[] = [];

    toggleDropdown(index: number) {
      this.closeAllDropdowns()
      this.isDropdownOpen[index] = !this.isDropdownOpen[index];
    }

    closeAllDropdowns() {
      this.isDropdownOpen = [];
    }
  

    @HostListener('document:click', ['$event'])
    closeDropdownOnClickOutside(event: MouseEvent) {
      if (!(event.target as HTMLElement).closest('.dropdown')) {
        this.closeAllDropdowns();
      }
    }


    getDownloadUrl(file: any): string {
      return `http://localhost:8000/web/download/${file}`; 
    }
    
    isRenameOpen = false;
    selected_file : File_ | any
    selected_file_ext : string = '';

    Rename(file:File_){
      this.selected_file = file
      this.isRenameOpen = true
    }

    Delete(fileId:number){
      this.confirmBoxEvokeService.danger('Confirm delete!', 'Are you sure you want to delete it?', 'Confirm', 'Decline')
      .subscribe(resp => {
        if (resp.success===true) {
          this.SiteService.deleteFile(fileId).pipe(take(1)).subscribe((data:unknown) =>{
            this.Files = this.Files.filter((item:any)=> item.id != fileId)
          },(error) =>{
            console.error(error);
          })          
        }
      });

    }

    closeRenamePanel(){
      this.isRenameOpen = false;
    }

    onRenameFile(form :NgForm, file_name : string,fileId:number){
      const fileExtension = file_name.split('.').pop();
      let new_name = `${form.value['edit-name']}.${fileExtension}`
      
      this.SiteService.renameFile(new_name,fileId).pipe(take(1)).subscribe((data:unknown) =>{
        this.selected_file.name = new_name
        this.closeRenamePanel();
      },(error) =>{
        console.error(error);
        
      })
    }

    draggedFile: any;

  onDragStart(event: DragEvent, file: any) {
    this.draggedFile = file;
    event.dataTransfer?.setData('text/plain', file.name);
  }

  onDragOver(event: DragEvent) {
    event.preventDefault(); 
  }

  onDrop(event: DragEvent, folder: Folder | any) {
    event.preventDefault(); 

    let folder_  = {
      id : -1,
    }
    
    if (folder.id == null){
      folder_.id = Number(this.path_ids[folder-1])      
    }
    else{
      folder_.id = folder.id
    }
    

    if (this.draggedFile) {
      this.SiteService.moveFile(folder_.id,this.draggedFile.id).pipe(take(1)).subscribe((data:unknown)=>{
        this.ngOnInit();
        this.draggedFile = null;   
      },(error)=>{
        console.error(error);
        this.draggedFile = null;
      })
    }
  }

}



