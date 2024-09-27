import { Component, OnInit } from '@angular/core';
import { TeamService } from '../Services/team.service';
import { ActivatedRoute, Router } from '@angular/router';
import { take } from 'rxjs';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-join-team',
  templateUrl: './join-team.component.html',
  styleUrls: ['./join-team.component.scss']
})
export class JoinTeamComponent implements OnInit{

  constructor(private teamService:TeamService,private router:Router,private route:ActivatedRoute,private toast:ToastrService){}

  ngOnInit(){
    this.teamService.joinTeam(this.route.snapshot.params['code']).pipe(take(1)).subscribe((data:any)=>{

    this.toast.success(data.reponse)
    this.router.navigate(['/'])
      
    },(error => {
      if (error.status == 400)
        this.toast.warning(error.error.Error)
      if (error.status == 409)
        this.toast.info(error.error.Error)
      if(error.status == 404)
        this.toast.error('Invalid link!')
      this.router.navigate(['/'])
    }))
  }
}
