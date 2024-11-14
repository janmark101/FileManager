import { Component, HostListener, OnInit, Type } from '@angular/core';
import { SiteService } from '../Services/site.service';
import { take } from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';
import { faChevronLeft } from '@fortawesome/free-solid-svg-icons';
import { Folder, Team } from '../Models/Models';
import {
  ConfirmBoxEvokeService,
  
} from '@costlydeveloper/ngx-awesome-popup';
import { NgForm } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';



@Component({
  selector: 'app-team',
  templateUrl: './team.component.html',
  styleUrls: ['./team.component.scss']
})
export class TeamComponent implements OnInit{

  Folders : Folder[] = []
  accTeam : Team = {
    id : 0,
    name : "0",
    "users" : [],
    created_at :  new Date(),
    user : 0
  }

  path = [];

  backIcon = faChevronLeft;
  currentPath: string[] = [];

  isAddFolderOpen : boolean = false;
  
  draggedFileFolder: any;
  isRenameOpen = false;
  selected_file_folder : Folder | any

  isDropdownFolderOpen: boolean[] = [];
  isDropdownAddOpen : boolean = false;
  team_id : number = -1

  selectedPermission : string = "Default"
  permissions :string[] = ["No Access", "Default", "Part Access" , "Full Access"]

  isMenagePermissionOpen : boolean = false

  ResourcePermissions : any[] =  []

  constructor(private SiteService:SiteService, private route:ActivatedRoute, private router: Router,private confirmBoxEvokeService: ConfirmBoxEvokeService,private toast:ToastrService) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params=>{
      this.team_id = Number(params.get('id'))
      
      if (this.team_id)
        this.fetchFolders(this.team_id);
    })

    this.route.params.subscribe(params => {
      this.currentPath = this.buildPath(params['id']);
    });
    
  }

  buildPath(initialId: string): string[] {
    return [initialId]; 
  }

  fetchFolders(id:number){
    this.SiteService.getFolders(id).pipe(take(1)).subscribe((data:any) =>{
      this.Folders = data.folders;
      this.accTeam = data.team;
    },(error:any) =>{
      console.error(error);
      
    })
  }

  navigateToSubfolder(folderId: number): void {    
    this.SiteService.checkFolderPermission(this.accTeam.id,folderId,['Default','Part Access','Full Access']).pipe(take(1)).subscribe((data=>{ 
      console.log(data);
           
      this.currentPath.push(folderId.toString());
      this.router.navigate([`/teams`, ...this.currentPath]);
    }),error=>{   

      if (error.status == 401){
        this.toast.error(error.error.Error)
      }
    })
  
  }


  onDragStart(event: DragEvent, obj: Folder) {
    this.draggedFileFolder = obj;
    event.dataTransfer?.setData('text/plain', obj.name);
  }

  onDragOver(event: DragEvent) {
    event.preventDefault(); 
  }

  onDrop(event: DragEvent, folder: Folder | any) {
    event.preventDefault(); 

    if (this.draggedFileFolder.id != folder.id)
      this.move_folder(folder.id)
  }

  move_folder(folderId:number){
    if (this.draggedFileFolder) {
      this.SiteService.checkFolderPermission(this.accTeam.id,this.draggedFileFolder.id,['Part Access','Full Access']).pipe(take(1)).subscribe((data=>{ 
        this.SiteService.moveFolder(folderId,this.draggedFileFolder.id).pipe(take(1)).subscribe((data:unknown)=>{
          this.ngOnInit();
          this.draggedFileFolder = null;   
        },(error)=>{
          console.error(error);
          this.draggedFileFolder = null;
        })
      }),error=>{   
        this.toast.error(error.error.Error)
      }
    )
    }
  }



  RenameFolder(folder:Folder){
    this.SiteService.checkFolderPermission(this.accTeam.id,folder.id,['Part Access','Full Access']).pipe(take(1)).subscribe((data=>{ 
      this.closeAllDropdowns();
      this.selected_file_folder = folder
      this.isRenameOpen = true
    }),error=>{   
        this.toast.error(error.error.Error)
      }
    )
  }

  DeleteFolder(folderId:number){
    this.SiteService.checkFolderPermission(this.accTeam.id,folderId,['Full Access']).pipe(take(1)).subscribe((data=>{ 
      this.closeAllDropdowns();
      this.confirmBoxEvokeService.danger('Confirm delete!', 'Are you sure you want to delete it?', 'Confirm', 'Decline')
      .subscribe(resp => {
        if (resp.success===true) {
          this.SiteService.deleteFolder(folderId).pipe(take(1)).subscribe((data:unknown) =>{
            this.ngOnInit();
            this.toast.success('Folder deleted!')
          },(error) =>{
            console.error(error);
            
          })          
        }
      });
    }),error=>{   
        this.toast.error(error.error.Error)
      }
    )
  }

  closePanel(){
    this.isRenameOpen = false;
    this.isAddFolderOpen = false;
    this.isMenagePermissionOpen = false;
  }

  onRenameFileFolder(form :NgForm, file_name : string,fileId:number){
    this.closeAllDropdowns();
    
      this.SiteService.renameFolder(form.value['edit-name'],fileId).pipe(take(1)).subscribe((data:unknown) =>{
        this.selected_file_folder.name = form.value['edit-name']
        this.closePanel();
      },(error) =>{
        this.toast.error('Something went wrong!');
        
      })
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
  this.isDropdownFolderOpen = [];
  this.isDropdownAddOpen = false;
}

@HostListener('document:click', ['$event'])
closeDropdownOnClickOutside(event: MouseEvent) {
  if (!(event.target as HTMLElement).closest('.dropdown') && !(event.target as HTMLElement).closest('.new')) {
    this.closeAllDropdowns();
  }
}



addFolder(){
  this.closeAllDropdowns();
  this.selectedPermission = "Default";
  this.isAddFolderOpen = true
}

onAddFolder(form :NgForm){
  
  this.SiteService.addFolder(form.value['folder-name'],'None',this.team_id,this.selectedPermission).pipe(take(1)).subscribe((data:unknown) =>{
    this.ngOnInit();
    this.closePanel();
    this.toast.success('Folder created!')
  },(error) =>{
    this.toast.error(error.error.error);
    
    
  })
}


onPermissionChange(event: Event) {
  const selectedValue = (event.target as HTMLSelectElement).value;
  this.selectedPermission = selectedValue
  }


  ManagePermissions(folderId:any){
    this.SiteService.checkFolderPermission(this.accTeam.id,folderId,['Full Access']).pipe(take(1)).subscribe((data=>{ 
      this.SiteService.getPermissions(folderId).pipe(take(1)).subscribe((data:any)=>{
        this.closeAllDropdowns();
        this.isMenagePermissionOpen = true
        console.log(data);
        
        this.ResourcePermissions = data.permissions
      },(error)=>{
        this.toast.error('Something went wrong!')
      })
    }),error=>{   
      this.toast.error(error.error.Error)
    }
  )
    
  }


  onManagePermissions(){

  }

}
