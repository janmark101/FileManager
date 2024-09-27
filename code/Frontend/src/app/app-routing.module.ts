import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomePageComponent } from './Site/home-page/home-page.component';
import { TeamComponent } from './Site/team/team.component';
import { SubFolderComponent } from './Site/sub-folder/sub-folder.component';
import { TeamSettingsComponent } from './Site/team-settings/team-settings.component';
import { LoginComponent } from './Site/login/login.component';
import { RegisterComponent } from './Site/register/register.component';
import { AuthGuard } from './Site/Services/auth.guard';
import { JoinTeamComponent } from './Site/join-team/join-team.component';

  const routes: Routes = [
    {path:'', component:HomePageComponent, canActivate:[AuthGuard]},
    {path:'login',component:LoginComponent, canActivate:[AuthGuard]},
    {path:'register',component:RegisterComponent, canActivate:[AuthGuard]},
    {path:'teams/:id',component:TeamComponent, canActivate:[AuthGuard]},
    {path:'teams/:id/settings',component:TeamSettingsComponent,canActivate:[AuthGuard]},
    {path:'join/:code',component:JoinTeamComponent,canActivate:[AuthGuard]},
    {path:'**', component:SubFolderComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
