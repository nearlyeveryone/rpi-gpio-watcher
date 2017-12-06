import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import 'rxjs/add/operator/map'

import { AuthenticationService } from './authentication.service';
import { GpioControl } from './models/gpioControl';

@Injectable()
export class UserService {

  constructor(private http: HttpClient, private authService: AuthenticationService) { }

  getGpioControls():Observable<GpioControl[]> {
    Observable.interval(2000).switchMap(() => this.http.get<GpioControl[]>('/api/Gpio'))

    return this.http.get<GpioControl[]>('/api/Gpio');
  }

  addGpioControl(control: GpioControl):boolean {
    var success: boolean = false;
    this.http.post('/api/Gpio', control).subscribe(
      res => {
        success = true;
      },
      err => {
        success = false;
      }
    );
    return success;
  }

  updateGpioControl(control: GpioControl):boolean {
    var success: boolean = false;
    this.http.put('/api/Gpio', control).subscribe(
      res => {
        success = true;
      },
      err => {
        success = false;
      }
    );
    return success;
  }
  deleteGpioControl(id: number):boolean {
    var success: boolean = false;
    this.http.delete('/api/Gpio', {
      params: new HttpParams().set('id', id.toString())
    }).subscribe(
      res => {
        success = true;
      },
      err => {
        success = false;
      }
    );
    return success;
  }
  logout() {
    this.authService.logout();
  }
}
