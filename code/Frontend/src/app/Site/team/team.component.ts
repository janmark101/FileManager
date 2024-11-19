import { Component, HostListener, OnInit } from '@angular/core';
import { SiteService } from '../Services/site.service';
import { take } from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';
import { faChevronLeft } from '@fortawesome/free-solid-svg-icons';
import { createDefaultDropDownState, createDefaultModalState, createDefaultPermissionsData, DropDownState, ModalState, PermissionsDataState, Resource, ResourcePermissions, Team, User } from '../Models/Models';
import {
  ConfirmBoxEvokeService,
  
} from '@costlydeveloper/ngx-awesome-popup';
import { NgForm } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { TeamService } from '../Services/team.service';





@Component({
  selector: 'app-team',
  templateUrl: './team.component.html',
  styleUrls: ['./team.component.scss']
})
export class TeamComponent implements OnInit{

  Resources : Resource[] = []

  TeamDescription : Team = {
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

  path = [];

  backIcon = faChevronLeft;
  currentPath: string[] = [];

  isModalOpen : ModalState = createDefaultModalState();
  isDropDownOpen : DropDownState = createDefaultDropDownState();



  draggedResource: Resource  | null = null;

  selectedResource : Resource = {
    name : "",
    id : ""
  }

  userInfo : number = -2;

  permissionsData : PermissionsDataState = createDefaultPermissionsData();


  constructor(private SiteService:SiteService, private route:ActivatedRoute, private router: Router,private confirmBoxEvokeService: ConfirmBoxEvokeService, 
    private toast:ToastrService, private teamService: TeamService) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params=>{     
      this.fetchResourcesAndTeam(Number(params.get('id')));
    })

    this.route.params.subscribe(params => {
      this.currentPath = this.buildPath(params['id']);
    });

    
  }

  buildPath(initialId: string): string[] {
    return [initialId]; 
  }

  fetchResourcesAndTeam(teamID:number){
    this.SiteService.getResources(teamID).pipe(take(1)).subscribe((data:any) =>{
      this.Resources = data.resources;
      this.TeamDescription = data.team;
      this.userInfo = data.user;
      console.log(data.team);
      
    },(error:any) =>{
      
    })
  }

  navigateToSubResources(resourceID: string): void {    
    this.SiteService.checkResourcePermission(this.TeamDescription!.id,resourceID,['Default','Part Access','Full Access']).pipe(take(1)).subscribe((data=>{            
      this.currentPath.push(resourceID.toString());
      this.router.navigate([`/teams`, ...this.currentPath]);
    }),error=>{   
      if (error.status == 403){
        this.toast.error(error.error.Error)
      }
    })
  
  }


  closePanel(){
    this.isModalOpen = createDefaultModalState();
  }


  onDragResourceStart(event: DragEvent, resource: Resource) {
    this.draggedResource = resource;    
    event.dataTransfer?.setData('text/plain', resource.name);
  }


  onDragResourceOver(event: DragEvent) {
    event.preventDefault(); 
  }


  onDropResource(event: DragEvent, resource: Resource | any) {
    event.preventDefault(); 
    
    if (this.draggedResource!.id != resource.id)
      this.moveResource(resource.id)
  }


  moveResource(resourceID:string){
    if (this.draggedResource) {
      this.SiteService.checkResourcePermission(this.TeamDescription!.id,this.draggedResource!.id.toString(),['Part Access','Full Access']).pipe(take(1)).subscribe((data=>{ 
        this.SiteService.checkResourcePermission(this.TeamDescription!.id,resourceID,['Part Access', 'Full Access']).pipe(take(1)).subscribe((data => {
          this.SiteService.moveResource(resourceID,this.draggedResource!.id.toString()).pipe(take(1)).subscribe((data:unknown)=>{
              this.ngOnInit();
              this.draggedResource = null;   
          },(error)=>{
              this.draggedResource = null;
              this.toast.error('Something went wrong!')
            })
          }),(error) =>{
            this.toast.error(error.error.Error)
          }) 
        }),(error) =>{
        this.toast.error(error.error.Error)
      })
    }
  }



  renameResource(resource:Resource){
    this.SiteService.checkResourcePermission(this.TeamDescription!.id,resource.id,['Part Access','Full Access']).pipe(take(1)).subscribe((data=>{ 
      this.closeAllDropdowns();
      this.selectedResource = resource
      this.isModalOpen['isRename'] = true;
    }),error=>{   
        this.toast.error(error.error.Error)
      }
    )
  }


  onRenameResource(form :NgForm, resourceID:string){
    this.closeAllDropdowns();
    
      this.SiteService.renameResource(form.value['edit-name'],resourceID).pipe(take(1)).subscribe((data) =>{
        this.selectedResource.name = form.value['edit-name']
        this.closePanel();
      },(error) =>{
        this.toast.error('Something went wrong!');
        
      })
  }


  deleteResource(resourceID:string){
    this.SiteService.checkResourcePermission(this.TeamDescription!.id,resourceID,['Full Access']).pipe(take(1)).subscribe((data=>{ 
      this.closeAllDropdowns();
      this.confirmBoxEvokeService.danger('Confirm delete!', 'Are you sure you want to delete it?', 'Confirm', 'Decline')
      .subscribe(resp => {
        if (resp.success===true) {
          this.SiteService.deleteResource(resourceID).pipe(take(1)).subscribe((data:unknown) =>{
            this.ngOnInit();
            this.toast.info('Folder deleted!')
          },(error) =>{            
          })          
        }
      });
    }),error=>{   
        this.toast.error(error.error.Error)
      }
    )
  }


  addResource(){
    this.closeAllDropdowns();
    this.permissionsData['selectedPermission'] = "Default";
    this.isModalOpen['isAddResource'] = true;
  }


  onAddResource(form :NgForm){
    this.SiteService.addResource(form.value['folder-name'],'None',this.TeamDescription!.id,this.permissionsData['selectedPermission']).pipe(take(1)).subscribe((data:unknown) =>{
      this.ngOnInit();
      this.closePanel();
      this.toast.success('Folder created!')
    },(error) =>{
      this.toast.error(error.error.error);
    })
  }


  managePermissions(resource : Resource){
    this.SiteService.checkResourcePermission(this.TeamDescription!.id,resource.id,['Full Access']).pipe(take(1)).subscribe((data=>{ 
      this.SiteService.getPermissions(this.TeamDescription.id,resource.id).pipe(take(1)).subscribe((data:any)=>{
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
      this.SiteService.changeResourcePermissions(this.TeamDescription.id,this.selectedResource.id, this.permissionsData['ChangedResourcePermissions']).pipe(take(1)).subscribe((data =>{
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


  toggleDropdownResource(index: number) {
    this.closeAllDropdowns()
    this.isDropDownOpen['resource'][index] = !this.isDropDownOpen['resource'][index];
  }


  toggleDropDownAdd(){
    this.closeAllDropdowns()
    this.isDropDownOpen['add'] = !this.isDropDownOpen['add'];
    
  }


  closeAllDropdowns() {
    this.isDropDownOpen['resource'] = []
    this.isDropDownOpen['add'] = false;
  }


  @HostListener('document:click', ['$event'])
  closeDropdownOnClickOutside(event: MouseEvent) {
    if (!(event.target as HTMLElement).closest('.dropdown') && !(event.target as HTMLElement).closest('.new')) {
      this.closeAllDropdowns();
    }
  }


  onPermissionChange(event: Event) {
    const selectedValue = (event.target as HTMLSelectElement).value;
    this.permissionsData['selectedPermission'] = selectedValue
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
        this.teamService.deleteUser(this.TeamDescription!.id, this.userInfo).pipe(take(1)).subscribe((data:unknown) =>{
          this.toast.info('Team was abandoned')
          this.router.navigate([""])
        },(error =>{
          console.error(error);
        })) 
      }
    });
  }

}
