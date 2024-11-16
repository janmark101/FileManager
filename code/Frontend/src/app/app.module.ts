import { NgModule,APP_INITIALIZER  } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { HttpClientModule, provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { NavbarComponent } from './Site/navbar/navbar.component';
import { HomePageComponent } from './Site/home-page/home-page.component';
import { TeamComponent } from './Site/team/team.component';
import { SubFolderComponent } from './Site/sub-folder/sub-folder.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule } from '@angular/forms';
import {
  NgxAwesomePopupModule,
  DialogConfigModule,
  ConfirmBoxConfigModule,
  ToastNotificationConfigModule
} from '@costlydeveloper/ngx-awesome-popup';
import { TeamSettingsComponent } from './Site/team-settings/team-settings.component';
import { LoginComponent } from './Site/login/login.component';
import { RegisterComponent } from './Site/register/register.component';
import { ToastrModule } from 'ngx-toastr';
import { initializeKeycloak } from 'src/keycloak-init'; 
import { KeycloakAngularModule, KeycloakBearerInterceptor, KeycloakService } from 'keycloak-angular';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { JoinTeamComponent } from './Site/join-team/join-team.component';
import { DragDropModule } from '@angular/cdk/drag-drop';


@NgModule({
  declarations: [
    AppComponent,
    HomePageComponent,
    NavbarComponent,
    TeamComponent,
    SubFolderComponent,
    TeamSettingsComponent,
    LoginComponent,
    RegisterComponent,
    JoinTeamComponent,

  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    NgxAwesomePopupModule.forRoot(), 
    DialogConfigModule.forRoot(), 
    ConfirmBoxConfigModule.forRoot(), 
    ToastNotificationConfigModule.forRoot() ,
    BrowserAnimationsModule,
    ToastrModule.forRoot(),
    KeycloakAngularModule,  
    DragDropModule
  ],
  providers: [
    {
      provide: APP_INITIALIZER,
      useFactory: initializeKeycloak,
      multi: true,
      deps: [KeycloakService],
    },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: KeycloakBearerInterceptor,
      multi: true
    },
    provideHttpClient(
      withInterceptorsFromDi()
    )
],
  bootstrap: [AppComponent]
})
export class AppModule { }
