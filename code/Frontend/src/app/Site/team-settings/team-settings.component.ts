import { Component, OnInit } from '@angular/core';
import { TeamService } from '../Services/team.service';
import { Team } from '../Models/Models';
import { ActivatedRoute } from '@angular/router';
import { take } from 'rxjs';

@Component({
  selector: 'app-team-settings',
  templateUrl: './team-settings.component.html',
  styleUrls: ['./team-settings.component.scss']
})
export class TeamSettingsComponent implements OnInit{


  constructor(private teamService:TeamService, private route:ActivatedRoute) {}

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
    },(error => {
      console.error(error);
      
    }))
  }
}
