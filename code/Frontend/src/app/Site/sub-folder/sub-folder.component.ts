import { Component, ElementRef, HostListener, ViewChild } from '@angular/core';
import { take } from 'rxjs';
import { Team, File_,Resource, Response, ModalState, createDefaultModalState, ResourcePermissions, DropDownState, createDefaultDropDownState, SubDropDownState, PermissionsDataState, createDefaultPermissionsData } from '../Models/Models';
import { ActivatedRoute, Router } from '@angular/router';
import { SiteService } from '../Services/site.service';
import { NgForm } from '@angular/forms';
import {
  ConfirmBoxEvokeService,
  
} from '@costlydeveloper/ngx-awesome-popup';
import { ToastrService } from 'ngx-toastr';
import { TeamService } from '../Services/team.service';

@Component({
  selector: 'app-sub-folder',
  templateUrl: './sub-folder.component.html',
  styleUrls: ['./sub-folder.component.scss']
})

export class SubFolderComponent {

  resources : Resource[] = []
  files : File_[] = []

  teamDescription : Team = {
    id : -1,
    name : "",
    "users" : [],
    created_at :  new Date(),
    team_owner : {
      id : -1,
      first_name : '',
      email : '',
      last_name : '',
      username : '',
    },
    adding_link_code : "",
    description : ""
  }

  extIcons = ['csv','docx','exe','jpg','json','mp4','pdf','png','ppt','xml','js','txt','html','mp3','zip','ppt','pptx']

  path : string[] = []
  path_ids : string[] = []
  currentPath: string[] = [];


  isModalOpen : ModalState = createDefaultModalState();
  isDropDownOpen : SubDropDownState = {
    ...createDefaultDropDownState(),
    files : []
  };

  permissionsData : PermissionsDataState = createDefaultPermissionsData();

  selectedResource : Resource = {
    name : "",
    id : ""
  }

  draggedFileOrResource: File_ | Resource | null = null
  selectedFileOrResource : File_ | Resource | null = null;

  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;
 
  userInfo : number = -2;

  constructor(private SiteService:SiteService, private route:ActivatedRoute, private router: Router,private confirmBoxEvokeService: ConfirmBoxEvokeService,
    private toast:ToastrService, private teamService: TeamService) {}


  ngOnInit(): void {
    this.currentPath = this.router.url.split('/');
    this.fetchSubResourcesFiles();
  }

  fetchSubResourcesFiles(){    
    this.SiteService.getSubResourcesFiles(Number(this.currentPath[2]),this.currentPath.at(-1)).pipe(take(1)).subscribe((data:Response) =>{
      console.log(data);
      
      this.resources = data.resources;
      this.teamDescription = data.team;
      this.files = data.files;
      this.path = data.resource_names;
      this.path_ids = data.resource_ids
      this.userInfo = data.user;
      this.makePath();
    },(error:any) =>{
      if (error.status == 404)
        this.router.navigate([''])
    })
  }

  makePath(){
    this.path.unshift(this.teamDescription!.name)
  }

  navigateToSubResources(resourceID : string): void {
    this.SiteService.checkResourcePermission(this.teamDescription!.id,resourceID,['Default','Part Access','Full Access']).pipe(take(1)).subscribe((data=>{      
      let url = this.router.url + "/" + resourceID
      this.router.navigateByUrl(url).then(()=>{
        this.ngOnInit();
      })
    }),error=>{      
      if (error.status == 403){
        this.toast.error(error.error.Error)
      }
    })
  }

  navigateToUrl(resourceID : string){
    let index = this.path.indexOf(resourceID)
    let temp = this.currentPath.slice(1,index+3)

    let url = 'teams'
    
    for (let index = 1; index < temp.length; index++) {
      url +=  '/' +  temp[index] 
    }
    
    this.router.navigateByUrl(url).then(()=>{
      this.ngOnInit();
    })
  }


  getIconUrl(file: File_): string {   
    const fileExtension = file.name.split('.').pop();
    
    if (this.extIcons.includes(fileExtension!))
      return `assets/WebImages/icons/${fileExtension}.png`
    else
      return `assets/WebImages/icons/file.png`
  }


  onDragStart(event: DragEvent, obj: Resource | File_) {
    this.draggedFileOrResource = obj;
    event.dataTransfer?.setData('text/plain', obj.name);
  }
  
  onDragOver(event: DragEvent) {
    event.preventDefault(); 
  }

  
  onDrop(event: DragEvent, resource: Resource | number) {
    event.preventDefault(); 

    let tempResourceID = '' as string
    
    if (typeof resource === 'number'){
      tempResourceID = this.path_ids[resource - 1]
    }
    else {
      tempResourceID = resource.id
    }
       

    if ('file' in this.draggedFileOrResource!) {
      this.moveFile(tempResourceID);
    }
    else{
      if (this.draggedFileOrResource!.id != tempResourceID)
        this.moveResource(tempResourceID)
    }
  }
  
  
  moveFile(resourceID: string){
    let actualResouce = this.currentPath.at(-1)

    this.SiteService.checkResourcePermission(this.teamDescription!.id,actualResouce,['Part Access','Full Access']).pipe(take(1)).subscribe((data=>{ 
      this.SiteService.checkResourcePermission(this.teamDescription!.id,resourceID,['Part Access', 'Full Access']).pipe(take(1)).subscribe((data => {
        this.SiteService.moveFile(resourceID,this.draggedFileOrResource!.id).pipe(take(1)).subscribe((data:unknown)=>{
            this.ngOnInit();
            this.draggedFileOrResource = null;   
        },(error)=>{
            this.draggedFileOrResource = null;
            this.toast.error('Something went wrong!')
          })
        }),(error) =>{
          this.toast.error(error.error.Error)
        }) 
      }),(error) =>{
      this.toast.error(error.error.Error)
    })
  }

  moveResource(resourceID : string){    
    this.SiteService.checkResourcePermission(this.teamDescription!.id,this.draggedFileOrResource!.id.toString(),['Part Access','Full Access']).pipe(take(1)).subscribe((data=>{ 
      this.SiteService.checkResourcePermission(this.teamDescription!.id,resourceID,['Part Access', 'Full Access']).pipe(take(1)).subscribe((data => {
        this.SiteService.moveResource(resourceID,this.draggedFileOrResource!.id.toString(), this.teamDescription.id).pipe(take(1)).subscribe((data:unknown)=>{
            this.ngOnInit();
            this.draggedFileOrResource = null;   
        },(error)=>{
            this.draggedFileOrResource = null;
            this.toast.error('Something went wrong!')
          })
        }),(error) =>{
          this.toast.error(error.error.Error)
        }) 
      }),(error) =>{
      this.toast.error(error.error.Error)
    })
  }
  

  toggleDropdownFile(index : number) {
    this.closeAllDropdowns()
    this.isDropDownOpen['resource'][index] = !this.isDropDownOpen['resource'][index];
  }

  toggleDropdownFolder(index : number) {
    this.closeAllDropdowns()
    this.isDropDownOpen['files'][index] = !this.isDropDownOpen['files'][index];
  }

  toggleDropDownAdd(){
    this.closeAllDropdowns()
    this.isDropDownOpen['add'] = !this.isDropDownOpen['add'];
    
  }

  closeAllDropdowns() {
    this.isDropDownOpen['resource'] = [];
    this.isDropDownOpen['files'] = [];
    this.isDropDownOpen['add'] = false;
  }

  closePanel(){
    this.isModalOpen = createDefaultModalState();
  }
  

  @HostListener('document:click', ['$event'])
  closeDropdownOnClickOutside(event: MouseEvent) {
    if (!(event.target as HTMLElement).closest('.dropdown') && !(event.target as HTMLElement).closest('.new')) {
      this.closeAllDropdowns();
    }
  }


  getDownloadUrl(file : any): string {
    return `http://localhost:8000/web/download${file}`; 
  }
    

  // selected_file_folder : File_ | Resource | null = null;
  selected_file_ext : string = '';


  renameFile(file : File_){    
    this.selectedFileOrResource = file
    this.isModalOpen['isRename'] = true;
  }


  deleteFile(fileID : number){
    this.confirmBoxEvokeService.danger('Confirm delete!', 'Are you sure you want to delete it?', 'Confirm', 'Decline')
    .subscribe(resp => {
      if (resp.success===true) {
        this.SiteService.deleteFile(fileID).pipe(take(1)).subscribe((data:unknown) =>{
          this.ngOnInit();
          this.toast.info('File deleted!')
        },(error) =>{
          console.error(error);
        })          
      }
    });

  }


  renameResource(resource : Resource){  
    this.SiteService.checkResourcePermission(this.teamDescription!.id,resource.id,['Part Access','Full Access']).pipe(take(1)).subscribe((data=>{ 
      this.selectedFileOrResource = resource
      this.isModalOpen['isRename'] = true;
    }),(error) =>{
      this.toast.error(error.error.Error)
    })
  
  }


  onRenameFileResource(form :NgForm, file_name : string, resourceOrFileID : string | number){
    if ('file' in this.selectedFileOrResource!){
      const fileExtension = file_name.split('.').pop();
    let new_name = `${form.value['edit-name']}.${fileExtension}`
    
    this.SiteService.renameFile(new_name,resourceOrFileID).pipe(take(1)).subscribe((data:unknown) =>{
        this.selectedFileOrResource!.name = new_name
        this.closePanel();
      },(error) =>{
      })
    }
    else{
      this.SiteService.renameResource(form.value['edit-name'],resourceOrFileID.toString(), this.teamDescription.id).pipe(take(1)).subscribe((data:unknown) =>{
        this.selectedFileOrResource!.name = form.value['edit-name']
        this.closePanel();
      },(error) =>{
      })
    }
  }


  deleteResource(resourceID : string){
    this.SiteService.checkResourcePermission(this.teamDescription!.id,resourceID,['Full Access']).pipe(take(1)).subscribe((data=>{ 
      this.confirmBoxEvokeService.danger('Confirm delete!', 'Are you sure you want to delete it?', 'Confirm', 'Decline').subscribe(resp => {
        if (resp.success===true) {
          this.SiteService.deleteResource(resourceID, this.teamDescription.id).pipe(take(1)).subscribe((data:unknown) =>{
            this.ngOnInit();
            this.toast.success('Folder deleted!')
          },(error) =>{
            this.toast.error('Something went wrong!')
            })          
          }
        });
      }),(error) =>{
      this.toast.error(error.error.Error)
    })
  }


  addResource(){
    this.SiteService.checkResourcePermission(this.teamDescription!.id,this.currentPath.at(-1),['Part Access', 'Full Access']).pipe(take(1)).subscribe((data=>{ 
      this.closeAllDropdowns();
      this.permissionsData['selectedPermission'] = "Default";
      this.isModalOpen['isAddResource'] = true;
    }),(error) =>{
      this.toast.error(error.error.Error)
    })
  }


  onPermissionChange(event: Event) {
    const selectedValue = (event.target as HTMLSelectElement).value;
    this.permissionsData['selectedPermission'] = selectedValue
  }
  

  onAddResource(form :NgForm){
    let parentResource = this.currentPath.at(-1)
    
    this.SiteService.addResource(form.value['folder-name'],parentResource,this.teamDescription!.id,this.permissionsData['selectedPermission']).pipe(take(1)).subscribe((data:unknown) =>{
      this.ngOnInit();
      this.closePanel();
      this.toast.success('Folder created!')
    },(error) =>{
      this.toast.error(error.error.error);
    })
   }


  addFile(){
    this.SiteService.checkResourcePermission(this.teamDescription!.id,this.currentPath.at(-1),['Part Access', 'Full Access']).pipe(take(1)).subscribe((data=>{ 
      this.fileInput.nativeElement.click();
    }),(error) =>{
      this.toast.error(error.error.Error)
    })
  }


  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      let file = input.files[0]; 
      let resourceID = this.currentPath.at(-1)
      const formData = new FormData();
      formData.append('file',file)
        this.SiteService.addFile(formData,resourceID!).pipe(take(1)).subscribe((data:unknown)=>{
          this.ngOnInit();
          this.toast.success('File added!')
        },(error: Error) => {          
      })
    }
  }

 
  managePermissions(resource : Resource){
    this.SiteService.checkResourcePermission(this.teamDescription!.id,resource.id,['Full Access']).pipe(take(1)).subscribe((data=>{ 
      this.SiteService.getPermissions(this.teamDescription.id,resource.id).pipe(take(1)).subscribe((data:any)=>{
        this.closeAllDropdowns();
        this.isModalOpen['isManagePermission'] = true;
        this.selectedResource = resource
        this.permissionsData['ChangedResourcePermissions'] = []
        this.permissionsData['ResourcePermissions'] = data        
      },(error)=>{
        this.toast.error('Something went wrong!')
      })
    }),error=>{   
      this.toast.error(error.error.Error)
    }
  ) 
  }
    
    
  
  onManagePermissions(){
    if (this.permissionsData['ChangedResourcePermissions'].length >=1){
      this.SiteService.changeResourcePermissions(this.teamDescription.id,this.selectedResource.id, this.permissionsData['ChangedResourcePermissions']).pipe(take(1)).subscribe((data =>{
        this.closePanel()
        this.toast.success('Permissions changed!')
      }),error=>{
        this.toast.error('Something went wrong!')
      })
    }
    else{
      this.closePanel()
    }
  }
    
    
    
  getPermissionsForBox(permission: string) {
    return this.permissionsData['ResourcePermissions'].filter(perm => perm.permission === permission);
  }


  dragUser(event: DragEvent, perm: any) {
    event.dataTransfer?.setData('text/plain', JSON.stringify(perm));
  }


  allowDropUser(event: DragEvent) {
    event.preventDefault(); 
  }


  dropUser(event: DragEvent, permission: string) {
    event.preventDefault();
    const data = event.dataTransfer?.getData('text/plain');

    if (data) {
      const perm = JSON.parse(data);
      this.updateUserPermission(perm, permission);
    }
  }
    
    
  updateUserPermission(perm: any, permission : string) {
    const index = this.permissionsData['ResourcePermissions'].findIndex(item => item.user.id === perm.user.id)

    if (index != -1) {      
      if (this.permissionsData['ResourcePermissions'][index].permission == permission)
        return
      this.permissionsData['ResourcePermissions'][index].permission = permission
      this.permissionsData['ChangedResourcePermissions'].push(this.permissionsData['ResourcePermissions'][index])
    }
  }
    

  leaveTeam(){
    this.confirmBoxEvokeService.danger('Confirm delete!', 'Are you sure you want to leave this team?', 'Confirm', 'Decline')
    .subscribe(resp => {
      if (resp.success===true) {
        this.teamService.deleteUser(this.teamDescription!.id, this.userInfo).pipe(take(1)).subscribe((data:unknown) =>{
          this.toast.info('Team was abandoned')
          this.router.navigate([""])
        },(error =>{
          console.error(error);
        })) 
      }
    });
  }

}



