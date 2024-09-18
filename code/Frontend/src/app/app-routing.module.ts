import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomePageComponent } from './Site/home-page/home-page.component';
import { TeamComponent } from './Site/team/team.component';
import { SubFolderComponent } from './Site/sub-folder/sub-folder.component';
import { TeamSettingsComponent } from './Site/team-settings/team-settings.component';
import { LoginComponent } from './Site/login/login.component';
import { RegisterComponent } from './Site/register/register.component';


  const routes: Routes = [
    {path:'', component:HomePageComponent},
    {path:'login',component:LoginComponent},
    {path:'register',component:RegisterComponent},
    {path:'teams/:id',component:TeamComponent},
    {path:'teams/:id/settings',component:TeamSettingsComponent},
    // {path:'**', component:SubFolderComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
