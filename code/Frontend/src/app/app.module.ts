import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { HttpClient, HttpClientModule } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { NavbarComponent } from './Site/navbar/navbar.component';
import { HomePageComponent } from './Site/home-page/home-page.component';
import { TeamComponent } from './Site/team/team.component';
import { SubFolderComponent } from './Site/sub-folder/sub-folder.component';
// import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';  
import { FormsModule } from '@angular/forms';
import {
  NgxAwesomePopupModule,
  DialogConfigModule,
  ConfirmBoxConfigModule,
  ToastNotificationConfigModule
} from '@costlydeveloper/ngx-awesome-popup';

@NgModule({
  declarations: [
    AppComponent,
    HomePageComponent,
    NavbarComponent,
    TeamComponent,
    SubFolderComponent,

  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    NgxAwesomePopupModule.forRoot(), 
    DialogConfigModule.forRoot(), 
    ConfirmBoxConfigModule.forRoot(), 
    ToastNotificationConfigModule.forRoot() 
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
