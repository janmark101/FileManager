import { Component, OnInit } from '@angular/core';
import { TeamService } from '../Services/team.service';
import { Team } from '../Models/Models';
import { take } from 'rxjs';



@Component({
  selector: 'app-home-page',
  templateUrl: './home-page.component.html',
  styleUrls: ['./home-page.component.scss']
})
export class HomePageComponent implements OnInit {


  constructor (private TeamsService: TeamService) {}

  Teams : Team[] = [];

  ngOnInit(): void {
    this.FetchTeams()
  }

  FetchTeams(){
    this.TeamsService.getTeams().pipe(take(1)).subscribe((response:Team[])=>{
      this.Teams = response;
      console.log(this.Teams);
      
    }, (error) =>{
      console.error(error)
    });
    }

}

