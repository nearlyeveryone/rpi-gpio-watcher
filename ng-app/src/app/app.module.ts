import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule }    from '@angular/forms';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';

import {VgCoreModule} from 'videogular2/core';
import {VgControlsModule} from 'videogular2/controls';
import {VgOverlayPlayModule} from 'videogular2/overlay-play';
import {VgBufferingModule} from 'videogular2/buffering';
import { VgStreamingModule } from 'videogular2/streaming';

import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

import { AppComponent } from './app.component';
import { routing } from './app.routing';

import { HomeComponent } from './home/home.component';
import { EditModelContent } from './home/home.component';
import { LoginComponent } from './login/login.component';

import { AuthGuard } from './auth.guard';
import { AuthenticationService } from './authentication.service';
import { UserService } from './user.service';

import { AddHeaderInterceptor } from './header.interceptor';


@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    EditModelContent,
    LoginComponent
  ],
  entryComponents: [EditModelContent],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    routing,

    VgCoreModule,
    VgControlsModule,
    VgOverlayPlayModule,
    VgBufferingModule,
    VgStreamingModule,
    NgbModule.forRoot()

  ],
  providers: [
    AuthGuard,
    AuthenticationService,
    UserService,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AddHeaderInterceptor,
      multi: true,
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
