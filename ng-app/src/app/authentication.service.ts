import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import 'rxjs/add/operator/map'

interface TokenResponse {
  validTo: string;
  value: string;
}

@Injectable()
export class AuthenticationService {
  public token: string;

  constructor(private http: HttpClient) {
    var currentUser = JSON.parse(localStorage.getItem('currentUser'));
    this.token = currentUser && currentUser.token;
   }

   login(password: string):Observable<boolean> {
     return this.http.post<TokenResponse>('/api/Token'
     , JSON.stringify({password: password})
     , { headers: new HttpHeaders().set('Content-Type', 'application/json')})
      .map(response => {
        let newToken = response.value;
        if(!(newToken === null)) {
          this.token = newToken;
          localStorage.setItem('currentUser', JSON.stringify({token: newToken}));

          return true;
        } else {
          return false;
        }
      });
   }
   logout(): void {
     this.token = null;
     localStorage.removeItem('currentUser');
   }
}
