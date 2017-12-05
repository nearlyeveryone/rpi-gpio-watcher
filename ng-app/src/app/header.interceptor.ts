import {Injectable, Injector} from '@angular/core';
import {
    HttpEvent,
    HttpInterceptor,
    HttpHandler,
    HttpRequest,
  } from '@angular/common/http';
  import { Observable } from 'rxjs';

  import { AuthenticationService } from './authentication.service';
  
@Injectable()
export class AddHeaderInterceptor implements HttpInterceptor {

    constructor(private injector: Injector) { }

    intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        //console.log("header modified");
        const authService = this.injector.get(AuthenticationService);
        // Clone the request to add the new header
        const clonedRequest = req.clone({ headers: req.headers.set('Authorization', 'Bearer ' + authService.token) });

        // Pass the cloned request instead of the original request to the next handle
        return next.handle(clonedRequest);
    }
}