import { Component, OnInit, Type } from '@angular/core';
import { SiteService } from '../Services/site.service';
import { take } from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';
import { faChevronLeft } from '@fortawesome/free-solid-svg-icons';
import { Folder, Team } from '../Models/Models';


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



  backIcon = faChevronLeft;
  currentPath: string[] = [];
  constructor(private SiteService:SiteService, private route:ActivatedRoute, private router: Router) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params=>{
      const team_id = Number(params.get('id'))
      
      if (team_id)
        this.fetchFolders(team_id);
    })

    this.route.params.subscribe(params => {
      this.currentPath = this.buildPath(params['id']);
    });

    console.log(this.currentPath);
    
  }

  buildPath(initialId: string): string[] {
    // Rozpocznij ścieżkę od initialId
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
    this.currentPath.push(folderId.toString());

    this.router.navigate([`/teams`, ...this.currentPath]);
  }

}
