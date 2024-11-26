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

  error : string = 'Name must be max 50   long';

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
      console.log(response);
      
    }, (error) =>{

    });
    }


  openAddTeamPanel(){
    this.isAddTeamOpen = true
    this.error = 'Name must be max 50 letters long';
    
  }

  closePanel(){
    this.isAddTeamOpen = false;
  }

  onAddTeam(form:NgForm){
    if (form.value['team-name'].length >50) {
      this.error = 'za dluga nzawa';
      return
    }

    let data = {
      "name" : form.value['team-name'],
      "description" : form.value['team-description'],
      "users" : [],
    }

    this.TeamsService.addTeam(data).pipe(take(1)).subscribe((data:unknown) => {
      this.ngOnInit();
    },(error:Error)=>{
      
    })
  }

}

