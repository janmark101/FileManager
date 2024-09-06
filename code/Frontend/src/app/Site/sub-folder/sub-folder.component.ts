import { Component, ElementRef, HostListener, ViewChild } from '@angular/core';
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
  isDropdownAddOpen : boolean = false;
  isAddFolderOpen : boolean = false;
  team_id : number = -1

  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;
 
  constructor(private SiteService:SiteService, private route:ActivatedRoute, private router: Router,private confirmBoxEvokeService: ConfirmBoxEvokeService) {}

  ngOnInit(): void {
    this.Folders = []
    this.Files  = []
    this.currentPath = this.router.url.split('/');
    this.path = [];
    this.path_ids = [];
    this.team_id = Number(this.currentPath[2])
    this.fetchSubFoldersFiles();
  }

  fetchSubFoldersFiles(){    
    this.SiteService.getSubFoldersFiles(Number(this.currentPath[2]),Number(this.currentPath.at(-1))).pipe(take(1)).subscribe((data:Response) =>{
      
      this.Folders = data.folders;
      this.accTeam = data.team;
      this.Files = data.files;
      this.path = data.folder_names_ids[0];
      this.path_ids = data.folder_names_ids[1]
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

    isDropdownFileOpen: boolean[] = [];
    isDropdownFolderOpen: boolean[] = [];

    toggleDropdownFile(index: number) {
      this.closeAllDropdowns()
      this.isDropdownFileOpen[index] = !this.isDropdownFileOpen[index];
    }

    toggleDropdownFolder(index: number) {
      this.closeAllDropdowns()
      this.isDropdownFolderOpen[index] = !this.isDropdownFolderOpen[index];
    }

    toggleDropDownAdd(){
      this.closeAllDropdowns()
      this.isDropdownAddOpen = !this.isDropdownAddOpen;
      console.log(this.isDropdownAddOpen);
      
    }

    closeAllDropdowns() {
      this.isDropdownFileOpen = [];
      this.isDropdownFolderOpen = [];
      this.isDropdownAddOpen = false;
    }

    closePanel(){
      this.isRenameOpen = false;
      this.isAddFolderOpen = false;
    }
  

    @HostListener('document:click', ['$event'])
    closeDropdownOnClickOutside(event: MouseEvent) {
      if (!(event.target as HTMLElement).closest('.dropdown') && !(event.target as HTMLElement).closest('.new')) {
        this.closeAllDropdowns();
      }
    }


    getDownloadUrl(file: any): string {
      return `http://localhost:8000/web/download/${file}`; 
    }
    
    isRenameOpen = false;
    selected_file_folder : File_ | Folder | any
    selected_file_ext : string = '';

    RenameFile(file:File_){
      this.selected_file_folder = file
      this.isRenameOpen = true
    }

    DeleteFile(fileId:number){
      this.confirmBoxEvokeService.danger('Confirm delete!', 'Are you sure you want to delete it?', 'Confirm', 'Decline')
      .subscribe(resp => {
        if (resp.success===true) {
          this.SiteService.deleteFile(fileId).pipe(take(1)).subscribe((data:unknown) =>{
            this.ngOnInit();
          },(error) =>{
            console.error(error);
          })          
        }
      });

    }


    RenameFolder(folder:Folder){
      this.selected_file_folder = folder
      this.isRenameOpen = true
    }

    DeleteFolder(folderId:number){
      this.confirmBoxEvokeService.danger('Confirm delete!', 'Are you sure you want to delete it?', 'Confirm', 'Decline')
      .subscribe(resp => {
        if (resp.success===true) {
          this.SiteService.deleteFolder(folderId).pipe(take(1)).subscribe((data:unknown) =>{
            this.ngOnInit();
          },(error) =>{
            console.error(error);
          })          
        }
      });

    }

    closeRenamePanel(){
      this.isRenameOpen = false;
    }

    onRenameFileFolder(form :NgForm, file_name : string,fileId:number){

      if (this.selected_file_folder.parent_folder){
        this.SiteService.renameFolder(form.value['edit-name'],fileId).pipe(take(1)).subscribe((data:unknown) =>{
          this.selected_file_folder.name = form.value['edit-name']
          this.closeRenamePanel();
        },(error) =>{
          console.error(error);
          
        })
      }
      else{

      const fileExtension = file_name.split('.').pop();
      let new_name = `${form.value['edit-name']}.${fileExtension}`
      
      this.SiteService.renameFile(new_name,fileId).pipe(take(1)).subscribe((data:unknown) =>{
        this.selected_file_folder.name = new_name
        this.closeRenamePanel();
      },(error) =>{
        console.error(error);
        
      })
    }
  }

    draggedFileFolder: any;

  onDragStart(event: DragEvent, obj: Folder | File_) {
    this.draggedFileFolder = obj;
    event.dataTransfer?.setData('text/plain', obj.name);
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

    if (this.draggedFileFolder.parent_folder) {
      if(this.draggedFileFolder.id != folder_.id)
        this.move_folder(folder_.id);
    }
    else{
      this.move_file(folder_.id);
    }
  }


  move_file(folderId:number){
    if (this.draggedFileFolder) {
      this.SiteService.moveFile(folderId,this.draggedFileFolder.id).pipe(take(1)).subscribe((data:unknown)=>{
        this.ngOnInit();
        this.draggedFileFolder = null;   
      },(error)=>{
        console.error(error);
        this.draggedFileFolder = null;
      })
    }
  }

  move_folder(folderId:number){
    if (this.draggedFileFolder) {
      this.SiteService.moveFolder(folderId,this.draggedFileFolder.id).pipe(take(1)).subscribe((data:unknown)=>{
        this.ngOnInit();
        this.draggedFileFolder = null;   
      },(error)=>{
        console.error(error);
        this.draggedFileFolder = null;
      })
    }
  }

  addFolder(){
    this.closeAllDropdowns();
    this.isAddFolderOpen = true
  }
  
  onAddFolder(form :NgForm){
    let parent_folder = Number(this.currentPath.at(-1))
    
    
    this.SiteService.addFolder(form.value['folder-name'],parent_folder,this.team_id).pipe(take(1)).subscribe((data:unknown) =>{
      this.ngOnInit();
      this.closePanel();
    },(error) =>{
      console.error(error);
      
    })
   }

   addFile(){
    this.fileInput.nativeElement.click();
   }

   onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      let file = input.files[0]; 
      let folder_id = Number(this.currentPath.at(-1))
      const formData = new FormData();
      formData.append('file',file)
        this.SiteService.addFile(formData,folder_id).pipe(take(1)).subscribe((data:unknown)=>{
          this.ngOnInit();
          
        },(error: Error) => {
          console.error(error);
          
        })
    }
  }


}



