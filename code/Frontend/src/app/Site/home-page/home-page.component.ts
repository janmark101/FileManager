import { Component, OnInit } from '@angular/core';
import { TeamService } from '../Services/team.service';
import { Team } from '../Models/Models';
import { Subscription, take } from 'rxjs';
import { NgForm } from '@angular/forms';
import { SiteService } from '../Services/site.service';



@Component({
  selector: 'app-home-page',
  templateUrl: './home-page.component.html',
  styleUrls: ['./home-page.component.scss']
})
export class HomePageComponent implements OnInit {


  constructor (private TeamsService: TeamService,private SiteService:SiteService) {}

  Teams : Team[] = [];

  isAddTeamOpen : boolean = false;
  subscription: Subscription = new Subscription();

  ngOnInit(): void {
    this.FetchTeams()
    this.reset();
    this.subscription = this.SiteService.callNgOnInit$.subscribe(() => {
      this.ngOnInit();
    });
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  reset(){
    this.Teams = [];

    this.isAddTeamOpen = false;
  
  }

  FetchTeams(){
    this.TeamsService.getTeams().pipe(take(1)).subscribe((response:Team[])=>{
      this.Teams = response;
      
    }, (error) =>{

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
      this.ngOnInit();
    },(error:Error)=>{
      
    })
  }

}

