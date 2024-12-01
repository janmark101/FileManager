import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthServiceService } from '../Services/auth-service.service';
import { take } from 'rxjs';

@Component({
  selector: 'app-email-change',
  templateUrl: './email-change.component.html',
  styleUrls: ['./email-change.component.scss']
})
export class EmailChangeComponent implements OnInit{
 
  
  
  constructor(private route : ActivatedRoute, private Auth: AuthServiceService, private router: Router){}


  ngOnInit(): void {
    this.route.paramMap.subscribe(params=>{     
      this.changeEmail(params.get('data'))
    })   
  }

  response : boolean  | null = null;


  changeEmail(token : string | null){
    let data = {
      payload : {
        "email" : token
        } 
    }

    this.Auth.changeData(data).pipe(take(1)).subscribe((data=>{
      this.response = true;
    }), error =>{

      if (error.status == 402){
        this.response = false;
      }
      else{
        console.log(error);
        
        this.router.navigate([''])
      }
    })
  }
}
