import { Component, HostListener } from '@angular/core';
import { take } from 'rxjs';
import { Team, File_,Folder, Response } from '../Models/Models';
import { ActivatedRoute, Router } from '@angular/router';
import { SiteService } from '../Services/site.service';


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

  extIcons = ['csv','docx','exe','jpg','json-file','mp4','pdf','png','ppt','xml']

  path : string[] = []

  currentPath: string[] = [];
 
  constructor(private SiteService:SiteService, private route:ActivatedRoute, private router: Router) {}

  ngOnInit(): void {
    this.Folders = []
    this.Files  = []
    this.currentPath = [];
    this.path = [];
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
      this.path = data.folder_names;
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
      return `assets/WebImages/icons/default.png`
    }

    isDropdownOpen: boolean[] = [];

    toggleDropdown(index: number) {
      this.closeAllDropdowns()
      this.isDropdownOpen[index] = !this.isDropdownOpen[index];
    }

    closeAllDropdowns() {
      this.isDropdownOpen = [];
    }
  
    // HostListener na dokument, aby zamknąć dropdowny po kliknięciu poza nimi
    @HostListener('document:click', ['$event'])
    closeDropdownOnClickOutside(event: MouseEvent) {
      if (!(event.target as HTMLElement).closest('.dropdown')) {
        this.closeAllDropdowns();
      }
    }


    getDownloadUrl(file: any): string {
      return `http://localhost:8000/web/download/${file}`; // Upewnij się, że ścieżka jest poprawna
    }
    
    
    Rename(){

    }

    Delete(){

    }

}



