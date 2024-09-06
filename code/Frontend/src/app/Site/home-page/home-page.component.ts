import { Component, OnInit } from '@angular/core';
import { TeamService } from '../Services/team.service';
import { Team } from '../Models/Models';
import { take } from 'rxjs';
import { NgForm } from '@angular/forms';



@Component({
  selector: 'app-home-page',
  templateUrl: './home-page.component.html',
  styleUrls: ['./home-page.component.scss']
})
export class HomePageComponent implements OnInit {


  constructor (private TeamsService: TeamService) {}

  Teams : Team[] = [];

  isAddTeamOpen : boolean = false;


  ngOnInit(): void {
    this.FetchTeams()
    this.reset();
  }

  reset(){
    this.Teams = [];

    this.isAddTeamOpen = false;
  
  }

  FetchTeams(){
    this.TeamsService.getTeams().pipe(take(1)).subscribe((response:Team[])=>{
      this.Teams = response;
      console.log(this.Teams);
      
    }, (error) =>{
      console.error(error)
    });
    }


  openAddTeamPanel(){
    this.isAddTeamOpen = true
  }

  closePanel(){
    this.isAddTeamOpen = false;
  }

  onAddTeam(form:NgForm){
    let team_name = form.value['team-name']

    this.TeamsService.addTeam(team_name).pipe(take(1)).subscribe((data:unknown) => {
      console.log(data);
      this.ngOnInit();
    },(error:Error)=>{
      console.log(error);
      
    })
  }

}

