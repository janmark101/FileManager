import { Component, OnInit } from '@angular/core';
import { TeamService } from '../Services/team.service';
import { Team } from '../Models/Models';
import { ActivatedRoute, Route, Router } from '@angular/router';
import { take } from 'rxjs';
import {
  ConfirmBoxEvokeService,
  
} from '@costlydeveloper/ngx-awesome-popup';


@Component({
  selector: 'app-team-settings',
  templateUrl: './team-settings.component.html',
  styleUrls: ['./team-settings.component.scss']
})
export class TeamSettingsComponent implements OnInit{


  constructor(private teamService:TeamService, private route:ActivatedRoute,private confService : ConfirmBoxEvokeService, private router: Router) {}

  team : Team = {
    "id": -1,
    "name" : '',
    "users" : [],
    "created_at" : new Date(),
    "user" : -1
  }

  team_id : number = -1

  ngOnInit(): void {
    this.route.paramMap.subscribe(params=>{
      this.team_id = Number(params.get('id'))
      this.getTeam();
    })


  }

  getTeam(){
    this.teamService.getTeam(this.team_id).pipe(take(1)).subscribe((data:any) => {
      this.team = data
      console.log(this.team);
      
    },(error => {
      console.error(error);
      
    }))
  }


  deleteTeam(){
    this.confService.danger('Confirm delete!', 'Are you sure you want to delete it?', 'Confirm', 'Decline')
    .subscribe(resp => {
      if (resp.success===true) {
        this.teamService.deleteTeam(this.team.id).pipe(take(1)).subscribe((data:unknown) =>{
          this.router.navigate([""])
        },(error =>{
          console.error(error);
        })) 
      }
    });
  }
}

