import { Component, OnInit, Input } from '@angular/core';

import { UserService } from '../user.service'
import { GpioControl } from '../models/gpioControl'

import { NgbModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap/modal/modal-ref';
import { Observable } from 'rxjs';
import 'rxjs/add/operator/map'

interface EditModalResponse {
  gpioControl: GpioControl;
  delete: boolean;
}

@Component({
  selector: 'edit-modal-content',
  templateUrl: './edit-model-content.html'
})
export class EditModelContent {
  @Input() gpioControl:GpioControl;
  constructor(public activeModal: NgbActiveModal) {}
  
  getReturnControl(del: boolean):EditModalResponse {
    var res: EditModalResponse = {delete: del, gpioControl: this.gpioControl};
    return res;
  }
}

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  gpioControls: GpioControl[] = [];
  updateGpio: boolean = true;

  constructor(private userService: UserService, private modalService: NgbModal) { }

  ngOnInit() {
    Observable.interval(2000)
    .switchMap(() => this.userService.getGpioControls())
    .map(res => res)
    .subscribe(gpioControls => {
        if(this.updateGpio) {
          this.gpioControls = gpioControls;
          console.log(this.gpioControls)
        }
        
      });
  }

  toggleControl(i: number) {
    console.log(i);
    this.gpioControls[i].value = !this.gpioControls[i].value;

    this.userService.updateGpioControl(this.gpioControls[i]);
  }

  openEditModal(index: number) {
    this.updateGpio = false;
    var modalRef = this.modalService.open(EditModelContent);
    modalRef.componentInstance.gpioControl = this.gpioControls[index];
    modalRef.result.then((result) => {
      console.log(result);
      if(modalRef.result)
      {
        if(result.delete)
        {
          this.userService.deleteGpioControl(this.gpioControls[index].controlModelId);
          this.gpioControls.splice(index, 1);
        } else {
          this.gpioControls[index] = result.gpioControl;
          this.userService.updateGpioControl(this.gpioControls[index]);
        }
      }
      this.updateGpio = true;
    }, result => {this.updateGpio = true;}
    );
  }

  openAddModal() {
    this.updateGpio = false;
    var modalRef = this.modalService.open(EditModelContent);
    var newControl: GpioControl = {controlModelId: 0, description: "", status: "",tooltip: "", parameters: "", value: false};
    modalRef.componentInstance.gpioControl = newControl;
    modalRef.result.then((result) => {
      if(modalRef.result)
      {
        if(result.delete)
        {

        } else {
          this.gpioControls.push(result.gpioControl)
          this.userService.addGpioControl(result.gpioControl);
        }
      }
      this.updateGpio = true;
    }, result => {this.updateGpio = true;}
    );
  }

  logout()
  {
    this.userService.logout();
  }
}
