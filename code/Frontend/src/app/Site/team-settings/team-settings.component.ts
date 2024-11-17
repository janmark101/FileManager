import { Component, OnInit } from '@angular/core';
import { TeamService } from '../Services/team.service';
import { Team, User } from '../Models/Models';
import { ActivatedRoute, Route, Router } from '@angular/router';
import { take } from 'rxjs';
import {
  ConfirmBoxEvokeService,
  
} from '@costlydeveloper/ngx-awesome-popup';
import { ToastrService } from 'ngx-toastr';


@Component({
  selector: 'app-team-settings',
  templateUrl: './team-settings.component.html',
  styleUrls: ['./team-settings.component.scss']
})
export class TeamSettingsComponent implements OnInit{


  constructor(private teamService:TeamService, private route:ActivatedRoute,private confService : ConfirmBoxEvokeService, private router: Router, private toast:ToastrService) {}

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
    adding_link_code : ""
  }


  addingLinkWindow : boolean = false;
  addingLink : string = ''


  ngOnInit(): void {
    this.route.paramMap.subscribe(params=>{
      this.getTeam(Number(params.get('id')));
    })
  }


  getTeam(teamID : number){
    this.teamService.getTeam(teamID).pipe(take(1)).subscribe((data:any) => {
      this.teamDescription = data      
      console.log(data);
      
    },(error => {      
    }))
  }


  deleteTeam(){
    this.confService.danger('Confirm delete!', 'Are you sure you want to delete it?', 'Confirm', 'Decline')
    .subscribe(resp => {
      if (resp.success===true) {
        this.teamService.deleteTeam(this.teamDescription!.id).pipe(take(1)).subscribe((data:unknown) =>{
          this.router.navigate([""])
          this.toast.info('Team deleted!')
        },(error =>{
        })) 
      }
    });
  }


  generateLink(){
    this.teamService.generateAddingLink(this.teamDescription!.id).pipe(take(1)).subscribe((data:any) => {
      this.addingLink = `http://localhost:4200/join/${data.link}`
      this.addingLinkWindow = true;
    }, (error => {
      console.error(error);
      this.addingLink = '';
      this.addingLinkWindow = false;
    }))
  }


  closePanel(){
    this.addingLinkWindow = false;
  }


  deleteUser(user : User) {
    this.confService.danger('Confirm delete!', 'Are you sure you want to delete this user?', 'Confirm', 'Decline')
    .subscribe(resp => {
      if (resp.success===true) {
        this.teamService.deleteUser(this.teamDescription!.id, user.id).pipe(take(1)).subscribe((data:unknown) =>{
          this.ngOnInit();
        },(error =>{
          console.error(error);
        })) 
      }
    });
  }
}

